#!/usr/bin/python3

'''Updates the user ranking.'''

import argparse
import datetime
import logging
import os
import sys
from typing import Sequence, NamedTuple

import MySQLdb
import MySQLdb.cursors

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "."))
import lib.db   # pylint: disable=wrong-import-position
import lib.logs  # pylint: disable=wrong-import-position


class Cutoff(NamedTuple):
    '''Cutoff percentile for user ranking.'''
    percentile: float
    classname: str


def _default_date() -> datetime.date:
    today = datetime.date.today()
    return today.replace(day=1)


def _parse_date(s: str) -> datetime.date:
    today = datetime.datetime.strptime(s, '%Y-%m-%d').date()
    return today.replace(day=1)


def update_problem_accepted_stats(cur: MySQLdb.cursors.BaseCursor) -> None:
    '''Updates the problem accepted stats'''

    logging.info('Updating accepted stats for problems...')
    cur.execute('''
        UPDATE
            `Problems` AS `p`
        SET
            `p`.accepted = (
                SELECT
                    COUNT(DISTINCT `s`.`identity_id`)
                FROM
                    `Submissions` AS `s`
                INNER JOIN
                    `Runs` AS `r`
                ON
                    `r`.run_id = `s`.current_run_id
                INNER JOIN
                    `Identities` AS `i`
                ON
                    `i`.`identity_id` = `s`.`identity_id`
                INNER JOIN
                    `Users` AS `u`
                ON
                    `u`.`user_id` = `i`.`user_id`
                WHERE
                    `s`.`problem_id` = `p`.`problem_id` AND `r`.verdict = 'AC'
                    AND NOT EXISTS (
                        SELECT
                            `pf`.`problem_id`, `pf`.`user_id`
                        FROM
                            `Problems_Forfeited` AS `pf`
                        WHERE
                            `pf`.`problem_id` = `p`.`problem_id` AND
                            `pf`.`user_id` = `u`.`user_id`
                    )
                    AND NOT EXISTS (
                        SELECT
                            `a`.`acl_id`
                        FROM
                            `ACLs` AS `a`
                        WHERE
                            `a`.`acl_id` = `p`.`acl_id` AND
                            `a`.`owner_id` = `u`.`user_id`
                    )
            );
    ''')


def update_user_rank(cur: MySQLdb.cursors.BaseCursor) -> Sequence[float]:
    '''Updates the user ranking.'''

    cur.execute('DELETE FROM `User_Rank`;')
    logging.info('Updating user rank...')
    cur.execute('''
        SELECT
            `i`.`username`,
            `i`.`name`,
            `i`.`country_id`,
            `i`.`state_id`,
            `isc`.`school_id`,
            `i`.`identity_id`,
            `i`.`user_id`,
            COUNT(`p`.`problem_id`) AS `problems_solved_count`,
            SUM(ROUND(100 / LOG(2, `p`.`accepted` + 1) , 0)) AS `score`
        FROM
        (
            SELECT
                `iu`.`user_id`,
                `s`.`problem_id`
            FROM
                `Submissions` AS `s`
            INNER JOIN
                `Runs` AS `r`
            ON
                `r`.run_id = `s`.current_run_id
            INNER JOIN
                `Identities` AS `iu`
            ON
                `iu`.identity_id = `s`.identity_id
            WHERE
                `r`.verdict = 'AC' AND
                `s`.type = 'normal' AND
                `iu`.user_id IS NOT NULL
            GROUP BY
                `iu`.user_id, `s`.`problem_id`
        ) AS up
        INNER JOIN
            `Users` AS `u` ON `u`.`user_id` = `up`.`user_id`
        INNER JOIN
            `Problems` AS `p`
        ON `p`.`problem_id` = up.`problem_id` AND `p`.visibility > 0
        INNER JOIN
            `Identities` AS `i` ON `i`.`identity_id` = u.`main_identity_id`
        LEFT JOIN
            `Identities_Schools` AS `isc`
        ON
            `isc`.`identity_school_id` = `i`.`current_identity_school_id`
        WHERE
            `u`.`is_private` = 0
            AND NOT EXISTS (
                SELECT
                    `pf`.`problem_id`, `pf`.`user_id`
                FROM
                    `Problems_Forfeited` AS `pf`
                WHERE
                    `pf`.`problem_id` = `p`.`problem_id` AND
                    `pf`.`user_id` = `u`.`user_id`
            )
            AND NOT EXISTS (
                SELECT
                    `a`.`acl_id`
                FROM
                    `ACLs` AS `a`
                WHERE
                    `a`.`acl_id` = `p`.`acl_id` AND
                    `a`.`owner_id` = `u`.`user_id`
            )
        GROUP BY
            `identity_id`
        ORDER BY
            `score` DESC;
    ''')
    prev_score = None
    rank = 0
    # MySQL has no good way of obtaining percentiles, so we'll store the sorted
    # list of scores in order to calculate the cutoff scores later.
    scores = []
    for index, row in enumerate(cur):
        if row['score'] != prev_score:
            rank = index + 1
        scores.append(row['score'])
        prev_score = row['score']
        cur.execute('''
                    INSERT INTO
                        `User_Rank` (`user_id`, `ranking`,
                                     `problems_solved_count`, `score`,
                                     `username`, `name`, `country_id`,
                                     `state_id`, `school_id`)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);''',
                    (row['user_id'], rank, row['problems_solved_count'],
                     row['score'], row['username'], row['name'],
                     row['country_id'], row['state_id'], row['school_id']))
    return scores


def update_author_rank(cur: MySQLdb.cursors.BaseCursor) -> None:
    '''Updates the author's ranking'''
    logging.info('Updating authors ranking...')
    cur.execute('''
        SELECT
            `u`.`user_id`,
            `i`.`username`,
            `i`.`name`,
            `i`.`country_id`,
            `i`.`state_id`,
            `isc`.`school_id`,
            SUM(`p`.`quality`) AS `author_score`
        FROM
            `Problems` AS `p`
        INNER JOIN
            `ACLs` AS `a` ON `a`.`acl_id` = `p`.`acl_id`
        INNER JOIN
            `Users` AS `u` ON `u`.`user_id` = `a`.`owner_id`
        INNER JOIN
            `Identities` AS `i` ON `i`.`identity_id` = `u`.`main_identity_id`
        LEFT JOIN
            `Identities_Schools` AS `isc`
        ON
            `isc`.`identity_school_id` = `i`.`current_identity_school_id`
        WHERE
            `p`.`quality` IS NOT NULL
        GROUP BY
            `u`.`user_id`
        ORDER BY
            `author_score` DESC
    ''')

    prev_score = None
    rank = 0
    for index, row in enumerate(cur):
        if row['author_score'] != prev_score:
            rank = index + 1
        prev_score = row['author_score']
        cur.execute('''
                    INSERT INTO
                        `User_Rank` (`user_id`, `username`, `author_score`,
                                     `author_ranking`, `name`, `country_id`,
                                     `state_id`, `school_id`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY
                        UPDATE
                            author_ranking = %s,
                            author_score = %s;''',
                    (row['user_id'], row['username'], row['author_score'],
                     rank, row['name'], row['country_id'], row['state_id'],
                     row['school_id'], rank, row['author_score']))


def update_user_rank_cutoffs(cur: MySQLdb.cursors.BaseCursor,
                             scores: Sequence[float]) -> None:
    '''Updates the user ranking cutoff table.'''

    cur.execute('DELETE FROM `User_Rank_Cutoffs`;')
    logging.info('Updating ranking cutoffs...')
    cutoffs = [
        Cutoff(.01, 'user-rank-international-master'),
        Cutoff(.09, 'user-rank-master'),
        Cutoff(.15, 'user-rank-expert'),
        Cutoff(.35, 'user-rank-specialist'),
        Cutoff(.40, 'user-rank-beginner'),
    ]
    if not scores:
        return
    for cutoff in cutoffs:
        # Scores are already in descending order. That will also bias the
        # cutoffs towards higher scores.
        cur.execute('''
                    INSERT INTO
                        `User_Rank_Cutoffs` (`score`, `percentile`,
                                             `classname`)
                    VALUES(%s, %s, %s);''',
                    (scores[int(len(scores) * cutoff.percentile)],
                     cutoff.percentile, cutoff.classname))


def update_schools_solved_problems(cur: MySQLdb.cursors.BaseCursor) -> None:
    '''Updates the solved problems count by each school the last 6 months'''

    logging.info('Updating schools solved problems...')

    months = 6  # in case this parameter requires adjustments
    cur.execute('DELETE FROM `Schools_Problems_Solved_Per_Month`')
    cur.execute('''
        INSERT INTO
            `Schools_Problems_Solved_Per_Month` (
                `school_id`,
                `time`,
                `problems_solved`
            )
        SELECT
            `sc`.`school_id`,
            STR_TO_DATE(
                CONCAT (
                    YEAR(`su`.`time`), '-', MONTH(`su`.`time`), '-01'
                ),
                "%%Y-%%m-%%d"
            ) AS `time`,
            COUNT(DISTINCT `su`.`problem_id`) AS `problems_solved`
        FROM
            `Submissions` AS `su`
        INNER JOIN
            `Schools` AS `sc` ON `sc`.`school_id` = `su`.`school_id`
        INNER JOIN
            `Runs` AS `r` ON `r`.`run_id` = `su`.`current_run_id`
        INNER JOIN
            `Problems` AS `p` ON `p`.`problem_id` = `su`.`problem_id`
        WHERE
            `su`.`time` >= CURDATE() - INTERVAL %s MONTH
            AND `r`.`verdict` = "AC" AND `p`.`visibility` >= 1
            AND NOT EXISTS (
                SELECT
                    *
                FROM
                    `Submissions` AS `sub`
                INNER JOIN
                    `Runs` AS `ru` ON `ru`.`run_id` = `sub`.`current_run_id`
                WHERE
                    `sub`.`problem_id` = `su`.`problem_id`
                    AND `sub`.`identity_id` = `su`.`identity_id`
                    AND `ru`.`verdict` = "AC"
                    AND `sub`.`time` < `su`.`time`
            )
        GROUP BY
            `sc`.`school_id`,
            `time`
        ORDER BY
            `time` ASC;
    ''', (months,))


def update_school_rank(cur: MySQLdb.cursors.BaseCursor) -> None:
    '''Updates the school rank'''

    logging.info('Updating school rank...')
    cur.execute('''
        SELECT
            `s`.`school_id`,
            SUM(ROUND(100 / LOG(2, `distinct_school_problems`.accepted+1), 0))
            AS `score`
        FROM
            `Schools` AS `s`
        INNER JOIN
            (
                SELECT
                    `su`.`school_id`,
                    `p`.accepted,
                    MIN(`su`.time)
                FROM
                    `Submissions` AS `su`
                INNER JOIN
                    `Runs` AS `r` ON `r`.run_id = `su`.current_run_id
                INNER JOIN
                    `Problems` AS `p` ON `p`.`problem_id` = `su`.`problem_id`
                WHERE
                    `r`.verdict = "AC"
                    AND `p`.visibility >= 1
                    AND `su`.`school_id` IS NOT NULL
                GROUP BY
                    `su`.`school_id`,
                    `su`.`problem_id`
            ) AS `distinct_school_problems`
        ON
            `distinct_school_problems`.`school_id` = `s`.`school_id`
        GROUP BY
            `s`.`school_id`
        ORDER BY
            `score` DESC;
    ''')
    prev_score = None
    rank = 0

    for index, row in enumerate(cur):
        if row['score'] != prev_score:
            rank = index + 1
        prev_score = row['score']
        cur.execute('''
                        UPDATE
                            `Schools` AS `s`
                        SET
                            `s`.`score` = %s,
                            `s`.`ranking` = %s
                        WHERE
                            `s`.`school_id` = %s;
                    ''',
                    (row['score'], rank, row['school_id']))


def update_school_of_the_month_candidates(
        cur: MySQLdb.cursors.BaseCursor,
        first_day_of_current_month: datetime.date) -> None:
    '''Updates the list of candidates to school of the current month'''

    logging.info('Updating the candidates to school of the month...')
    if first_day_of_current_month.month == 12:
        first_day_of_next_month = datetime.date(
            first_day_of_current_month.year + 1,
            1,
            1)
    else:
        first_day_of_next_month = datetime.date(
            first_day_of_current_month.year,
            first_day_of_current_month.month + 1,
            1)

    # First make sure there are not already selected schools of the month
    cur.execute('''
                SELECT
                    COUNT(*) AS `count`
                FROM
                    `School_Of_The_Month`
                WHERE
                    `time` = %s AND
                    `selected_by` IS NOT NULL;
                ''',
                (first_day_of_next_month,))

    for row in cur:
        if row['count'] > 0:
            logging.info('Skipping because already exist selected schools.')
            return

    cur.execute('''
                DELETE FROM
                    `School_Of_The_Month`
                WHERE
                    `time` = %s;
                ''',
                (first_day_of_next_month,))

    cur.execute(
        '''
        SELECT
            `s`.`school_id`,
            IFNULL(
                SUM(
                    ROUND(
                        100 / LOG(2, `distinct_school_problems`.`accepted`+1),
                        0
                    )
                ),
                0.0
            ) AS `score`
        FROM
            `Schools` AS `s`
        INNER JOIN
            (
                SELECT
                    `su`.`school_id`,
                    `p`.`accepted`,
                    MIN(`su`.`time`) AS `first_ac_time`
                FROM
                    `Submissions` AS `su`
                INNER JOIN
                    `Runs` AS `r` ON `r`.`run_id` = `su`.`current_run_id`
                INNER JOIN
                    `Problems` AS `p` ON `p`.`problem_id` = `su`.`problem_id`
                WHERE
                    `r`.`verdict` = "AC"
                    AND `p`.`visibility` >= 1
                    AND `su`.`school_id` IS NOT NULL
                GROUP BY
                    `su`.`school_id`,
                    `su`.`problem_id`
                HAVING
                    `first_ac_time` BETWEEN %s AND %s
            ) AS `distinct_school_problems`
        ON
            `distinct_school_problems`.`school_id` = `s`.`school_id`
        WHERE
            NOT EXISTS (
                SELECT
                    `sotm`.`school_id`,
                    MAX(`time`) AS `latest_time`
                FROM
                    `School_Of_The_Month` AS `sotm`
                WHERE
                    `sotm`.`school_id` = `s`.`school_id`
                    AND (
                        `sotm`.`selected_by` IS NOT NULL OR
                        `sotm`.`ranking` = 1
                    )
                GROUP BY
                    `sotm`.`school_id`
                HAVING
                    DATE_ADD(`latest_time`, INTERVAL 1 YEAR) >= %s
            )
        GROUP BY
            `s`.`school_id`
        ORDER BY
            `score` DESC
        LIMIT 100;
        ''',
        (
            first_day_of_current_month,
            first_day_of_next_month,
            first_day_of_next_month
        ))

    for index, row in enumerate(cur):
        cur.execute('''
                    INSERT INTO
                        `School_Of_The_Month` (
                            `school_id`,
                            `time`,
                            `ranking`,
                            `score`
                        )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s
                    );
                    ''',
                    (
                        row['school_id'],
                        first_day_of_next_month,
                        index + 1,
                        row['score']
                    ))


def update_coder_of_the_month_candidates(
        cur: MySQLdb.cursors.BaseCursor,
        first_day_of_current_month: datetime.date,
        category: str) -> None:
    '''Updates the list of candidates to coder of the current month'''

    logging.info('Updating the candidates to coder of the month...')
    if first_day_of_current_month.month == 12:
        first_day_of_next_month = datetime.date(
            first_day_of_current_month.year + 1,
            1,
            1)
    else:
        first_day_of_next_month = datetime.date(
            first_day_of_current_month.year,
            first_day_of_current_month.month + 1,
            1)

    # First make sure there are not already selected coder of the month
        cur.execute('''
                SELECT
                    COUNT(*) AS `count`
                FROM
                    `Coder_Of_The_Month`
                WHERE
                    `time` = %s AND
                    `selected_by` IS NOT NULL AND
                    `category` = %s;
                ''', (first_day_of_next_month, category))
    for row in cur:
        if row['count'] > 0:
            logging.info('Skipping because already exist selected coder')
            return
    cur.execute('''
                DELETE FROM
                    `Coder_Of_The_Month`
                WHERE
                    `time` = %s AND
                    `category` = %s;
                ''',
                (first_day_of_next_month, category))
    if category == 'female':
        gender_clause = " AND i.gender = 'female'"
    else:
        gender_clause = ""

    sql = f'''
         SELECT DISTINCT
            IFNULL(i.user_id, 0) AS user_id,
            i.username,
            IFNULL(i.country_id, 'xx') AS country_id,
            isc.school_id,
            COUNT(ps.problem_id) ProblemsSolved,
            IFNULL(SUM(ROUND(100 / LOG(2, ps.accepted+1) , 0)), 0) AS score,
            IFNULL(
                (
                    SELECT urc.classname FROM
                        User_Rank_Cutoffs urc
                    WHERE
                        urc.score <= (
                                SELECT
                                    ur.score
                                FROM
                                    User_Rank ur
                                WHERE
                                    ur.user_id = i.user_id
                            )
                    ORDER BY
                        urc.percentile ASC
                    LIMIT
                        1
                ),
                'user-rank-unranked'
            ) AS classname
          FROM
            (
              SELECT DISTINCT
                s.identity_id, s.problem_id
              FROM
                Submissions s
              INNER JOIN
                Runs r
              ON
                r.run_id = s.current_run_id
              WHERE
                r.verdict = 'AC' AND s.type= 'normal' AND
                s.time >= %s AND s.time <= %s
            ) AS up
          INNER JOIN
            Problems ps ON
            ps.problem_id = up.problem_id
            AND ps.visibility >= 1
            AND ps.quality_seal = 1
          INNER JOIN
            Identities i ON i.identity_id = up.identity_id
          LEFT JOIN
            Identities_Schools isc ON isc.identity_school_id =
            i.current_identity_school_id
          LEFT JOIN
            (
              SELECT
                user_id,
                MAX(time) latest_time,
                selected_by
              FROM
                Coder_Of_The_Month
              WHERE
                category = %s
              GROUP BY
                user_id,
                selected_by
            ) AS cm on i.user_id = cm.user_id
          WHERE
            (cm.user_id IS NULL OR
            DATE_ADD(cm.latest_time, INTERVAL 1 YEAR) < %s) AND
            i.user_id IS NOT NULL
            {gender_clause}
          GROUP BY
            up.identity_id
          ORDER BY
            score DESC,
            ProblemsSolved DESC
          LIMIT 100;
        '''
    cur.execute(
        sql,
        (
            first_day_of_current_month,
            first_day_of_next_month,
            category,
            first_day_of_next_month,
        ))

    for index, row in enumerate(cur):
        cur.execute('''
                    INSERT INTO
                        `Coder_Of_The_Month` (
                            `user_id`,
                            `time`,
                            `ranking`,
                            `school_id`,
                            `category`,
                            `score`,
                            `problems_solved`
                        )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    );
                    ''',
                    (
                        row['user_id'],
                        first_day_of_next_month,
                        index + 1,
                        row['school_id'],
                        category,
                        row['score'],
                        row['ProblemsSolved']
                    ))


def update_users_stats(
        cur: MySQLdb.cursors.BaseCursor,
        dbconn: MySQLdb.connections.Connection,
        date: datetime.date) -> None:
    '''Updates all the information and ranks related to users'''
    logging.info('Updating users stats...')
    try:
        try:
            scores = update_user_rank(cur)
            update_user_rank_cutoffs(cur, scores)
        except:  # noqa: bare-except
            logging.exception('Failed to update user ranking')
            raise

        try:
            update_author_rank(cur)
        except:  # noqa: bare-except
            logging.exception('Failed to update authors ranking')
            raise
        # We update both the general rank and the author's rank in the same
        # transaction since both are stored in the same DB table.
        dbconn.commit()

        try:
            update_coder_of_the_month_candidates(cur, date, 'all')
            dbconn.commit()
        except:  # noqa: bare-except
            logging.exception(
                'Failed to update candidates to coder of the month')
            raise

        try:
            update_coder_of_the_month_candidates(cur, date, 'female')
            dbconn.commit()
        except:  # noqa: bare-except
            logging.exception(
                'Failed to update candidates to coder of the month female')
            raise
        logging.info('Users stats updated')
    except:  # noqa: bare-except
        logging.exception('Failed to update all users stats')


def update_schools_stats(
        cur: MySQLdb.cursors.BaseCursor,
        dbconn: MySQLdb.connections.Connection,
        date: datetime.date) -> None:
    '''Updates all the information and ranks related to schools'''
    logging.info('Updating schools stats...')
    try:
        try:
            update_schools_solved_problems(cur)
            dbconn.commit()
        except:  # noqa: bare-except
            logging.exception('Failed to update schools solved problems')
            raise

        try:
            update_school_rank(cur)
            dbconn.commit()
        except:  # noqa: bare-except
            logging.exception('Failed to update school ranking')
            raise

        try:
            update_school_of_the_month_candidates(cur, date)
            dbconn.commit()
        except:  # noqa: bare-except
            logging.exception(
                'Failed to update candidates to school of the month')
            raise
        logging.info('Schools stats updated')
    except:  # noqa: bare-except
        logging.exception('Failed to update all schools stats')


def main() -> None:
    '''Main entrypoint.'''

    parser = argparse.ArgumentParser(description=__doc__)
    lib.db.configure_parser(parser)
    lib.logs.configure_parser(parser)

    parser.add_argument('--date',
                        type=_parse_date,
                        default=_default_date(),
                        help='The date the command should take as today')
    args = parser.parse_args()
    lib.logs.init(parser.prog, args)

    logging.info('Started')
    dbconn = lib.db.connect(args)
    try:
        with dbconn.cursor(cursorclass=MySQLdb.cursors.DictCursor) as cur:
            update_problem_accepted_stats(cur)
            update_users_stats(cur, dbconn, args.date)
            update_schools_stats(cur, dbconn, args.date)
    finally:
        dbconn.close()
        logging.info('Done')


if __name__ == '__main__':
    main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
