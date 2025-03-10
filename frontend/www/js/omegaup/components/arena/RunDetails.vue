<template>
  <form data-run-details-view>
    <div v-if="data">
      <button class="close">❌</button>
      <div v-if="inCourse && (data.admin || data.feedback)">
        <h3>{{ T.feedbackTitle }}</h3>
        <pre>{{
          data.feedback ? data.feedback.feedback : T.feedbackNotSentYet
        }}</pre>
        <div v-if="data.feedback">
          {{ T.feedbackLeftBy }}
          <omegaup-user-username
            :username="data.feedback.author"
            :classname="data.feedback.author_classname"
            :linkify="true"
          ></omegaup-user-username>
        </div>
        <div v-if="data.admin" class="feedback-section">
          <a role="button" @click="showFeedbackForm = !showFeedbackForm">{{
            data.feedback === null
              ? T.submissionFeedbackSendButton
              : T.submissionFeedbackUpdateButton
          }}</a>
          <div v-show="showFeedbackForm" class="form-group">
            <textarea
              v-model="feedback"
              class="form-control"
              rows="3"
              maxlength="200"
            ></textarea>
            <button
              class="btn btn-sm btn-primary"
              :disabled="!feedback"
              @click.prevent="
                $emit('set-feedback', {
                  guid: data.guid,
                  feedback,
                  isUpdate: data.feedback !== null,
                })
              "
            >
              {{
                data.feedback === null
                  ? T.submissionSendFeedback
                  : T.submissionUpdateFeedback
              }}
            </button>
          </div>
        </div>
      </div>
      <div v-if="data.groups" class="cases">
        <h3>{{ T.wordsCases }}</h3>
        <div></div>
        <table>
          <thead>
            <tr>
              <th>{{ T.wordsGroup }}</th>
              <th v-if="data.submissionFeedback !== 'summary'">
                {{ T.wordsCase }}
              </th>
              <th>{{ T.wordsVerdict }}</th>
              <th colspan="3">{{ T.rankScore }}</th>
              <th width="1"></th>
            </tr>
          </thead>
          <tbody v-for="element in data.groups" :key="element.group">
            <tr class="group">
              <th class="center">{{ element.group }}</th>
              <th v-if="element.verdict" class="text-center">
                {{ element.verdict }}
              </th>
              <th v-else colspan="2">
                <div class="dropdown-cases" @click="toggle(element.group)">
                  <font-awesome-icon
                    v-if="groupVisible[element.group]"
                    :icon="['fas', 'chevron-circle-up']"
                  />
                  <font-awesome-icon
                    v-else
                    :icon="['fas', 'chevron-circle-down']"
                  />
                </div>
              </th>
              <th class="score">
                {{
                  element.contest_score ? element.contest_score : element.score
                }}
              </th>
              <th class="center" width="10">
                {{ element.max_score ? '/' : '' }}
              </th>
              <th>{{ element.max_score ? element.max_score : '' }}</th>
            </tr>
            <template v-if="groupVisible[element.group]">
              <template v-for="problem_case in element.cases">
                <tr>
                  <td></td>
                  <td class="text-center">{{ problem_case.name }}</td>
                  <td class="text-center">{{ problem_case.verdict }}</td>
                  <td class="score">
                    {{
                      problem_case.contest_score
                        ? problem_case.contest_score
                        : problem_case.score
                    }}
                  </td>
                  <td class="center" width="10">
                    {{ problem_case.max_score ? '/' : '' }}
                  </td>
                  <td>
                    {{ problem_case.max_score ? problem_case.max_score : '' }}
                  </td>
                </tr>
                <template v-if="shouldShowDiffs(problem_case.name)">
                  <tr>
                    <td colspan="6">{{ T.wordsInput }}</td>
                  </tr>
                  <tr>
                    <td colspan="6">
                      <pre>{{
                        showDataCase(data.cases, problem_case.name, 'in')
                      }}</pre>
                    </td>
                  </tr>
                  <tr>
                    <td colspan="6">{{ T.wordsDifference }}</td>
                  </tr>
                  <tr>
                    <td v-if="data.cases" colspan="6">
                      <omegaup-arena-diff-view
                        :left="data.cases[problem_case.name].out"
                        :right="
                          getContestantOutput(data.cases, problem_case.name)
                        "
                      ></omegaup-arena-diff-view>
                    </td>
                    <td v-else colspan="6" class="empty-table-message">
                      {{ EMPTY_FIELD }}
                    </td>
                  </tr>
                </template>
              </template>
            </template>
          </tbody>
        </table>
      </div>
      <h3>{{ T.wordsSource }}</h3>
      <a v-if="data.source_link" download="data.zip" :href="data.source">{{
        T.wordsDownload
      }}</a>
      <omegaup-arena-code-view
        v-else
        :language="data.language"
        :readonly="true"
        :value="data.source"
      ></omegaup-arena-code-view>
      <div v-if="data.compile_error" class="compile_error">
        <h3>{{ T.wordsCompilerOutput }}</h3>
        <pre class="compile_error" v-text="data.compile_error"></pre>
      </div>
      <div v-if="data.logs" class="logs">
        <h3>{{ T.wordsLogs }}</h3>
        <pre v-text="data.logs"></pre>
      </div>
      <div class="download">
        <h3>{{ T.wordsDownload }}</h3>
        <ul>
          <li>
            <a
              class="sourcecode"
              :download="data.source_name"
              :href="data.source_url"
              >{{ T.wordsDownloadCode }}</a
            >
          </li>
          <li>
            <a
              v-if="data.admin"
              class="output"
              :href="`/api/run/download/run_alias/${data.guid}/`"
              >{{ T.wordsDownloadOutput }}</a
            >
          </li>
          <li>
            <a
              v-if="data.admin"
              class="details"
              :href="`/api/run/download/run_alias/${data.guid}/complete/true/`"
              >{{ T.wordsDownloadDetails }}</a
            >
          </li>
        </ul>
      </div>
      <div v-if="data.judged_by" class="judged_by">
        <h3>{{ T.wordsJudgedBy }}</h3>
        <pre v-text="data.judged_by"></pre>
      </div>
    </div>
  </form>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator';
import { types } from '../../api_types';
import T from '../../lang';
import * as ui from '../../ui';
import arena_CodeView from './CodeView.vue';
import arena_DiffView from './DiffView.vue';
import user_Username from '../user/Username.vue';

import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import {
  faChevronCircleUp,
  faChevronCircleDown,
} from '@fortawesome/free-solid-svg-icons';
library.add(faChevronCircleUp);
library.add(faChevronCircleDown);

interface GroupVisibility {
  [name: string]: boolean;
}

const EMPTY_FIELD = '∅';

@Component({
  components: {
    FontAwesomeIcon,
    'omegaup-arena-code-view': arena_CodeView,
    'omegaup-arena-diff-view': arena_DiffView,
    'omegaup-user-username': user_Username,
  },
})
export default class ArenaRunDetails extends Vue {
  @Prop() data!: types.RunDetails;
  @Prop({ default: false }) inCourse!: boolean;

  EMPTY_FIELD = EMPTY_FIELD;
  T = T;
  ui = ui;
  groupVisible: GroupVisibility = {};
  showFeedbackForm = false;
  feedback = this.data?.feedback?.feedback ?? null;

  toggle(group: string): void {
    const visible = this.groupVisible[group];
    this.$set(this.groupVisible, group, !visible);
  }

  showDataCase(
    cases: types.ProblemCasesContents,
    caseName: string,
    caseType: 'in' | 'out' | 'contestantOutput',
  ): string {
    return cases[caseName]?.[caseType] ?? EMPTY_FIELD;
  }

  shouldShowDiffs(caseName: string): boolean {
    return (
      this.data.show_diff === 'all' ||
      (caseName === 'sample' && this.data.show_diff === 'examples')
    );
  }

  getContestantOutput(cases: types.ProblemCasesContents, name: string): string {
    return cases[name]?.contestantOutput ?? '';
  }
}
</script>

<style lang="scss">
@import '../../../../sass/main.scss';

#overlay {
  display: none;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(var(--overlay-background-color), 0.5);
  z-index: 9999998 !important;

  form {
    background: var(--arena-run-details-form-background-color);
    width: 80%;
    height: 90%;
    margin: auto;
    border: 2px solid var(--arena-run-details-form-border-color);
    padding: 1em;
    position: absolute;
    overflow-y: auto;
    overflow-x: hidden;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    flex-direction: column;

    button.close {
      position: sticky;
      position: -webkit-sticky;
      top: 0;
      z-index: 100;
      right: 0;
      background-color: var(--arena-form-close-background-color);
      border: 1px solid var(--arena-form-close-border-color);
      border-width: 0 0 1px 1px;
      font-size: 110%;
      width: 25px;
      height: 25px;

      &:hover {
        background-color: var(--arena-form-close-background-color--hover);
      }
    }

    .languages {
      width: 100%;
    }

    .filename-extension {
      width: 100%;
    }

    .run-submit-paste-text {
      width: 100%;
    }

    .code-view {
      width: 100%;
      flex-grow: 1;
      overflow: auto;
    }

    .upload-file {
      width: 100%;
    }

    .submit-run {
      width: 100%;
    }
  }

  input[type='submit'] {
    font-size: 110%;
    padding: 0.3em 0.5em;
  }
}

.dropdown-cases {
  height: 100%;
  width: 100%;
  margin: 0 auto;
  text-align: center;
  background: var(--arena-run-details-dropdown-cases-background-color);
  border-radius: 5px;
}

#run-details .compile_error {
  display: none;
}

.guid {
  font-family: monospace;
  padding: 0 0.3em;
}

#run-details .logs {
  margin-top: 1em;
  border-top: 1px dotted black;
  padding-top: 1em;
  display: none;
}

.cases {
  table {
    width: 100%;

    tr.group {
      border-top: 1px solid var(--arena-cases-tr-border-top-color);

      td,
      th {
        padding: 0.2em inherit 0.2em inherit;
      }
    }

    thead th,
    td.center,
    th.center {
      text-align: center;
    }

    td.score,
    th.score {
      text-align: right;
    }

    pre.stderr {
      color: var(--arena-cases-table-stderr-font-color);
    }
  }

  span.collapse {
    padding: 0.2em;
  }
}

.feedback-section {
  margin-top: 1.5em;

  .form-group {
    margin-top: 0.5em;

    button {
      margin-top: 1em;
    }
  }
}
</style>
