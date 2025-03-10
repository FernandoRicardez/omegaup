<template>
  <div>
    <div class="page-header">
      <h1>
        {{
          ui.formatString(T.contestEditWithTitle, {
            title: ui.contestTitle(details),
          })
        }}
        <small>
          &ndash;
          <a :href="ui.contestURL(details)">
            {{ T.contestDetailsGoToContest }}</a
          >
        </small>
      </h1>
    </div>

    <ul class="nav nav-pills my-3">
      <li class="nav-item dropdown">
        <a
          href="#"
          data-toggle="dropdown"
          role="button"
          data-nav-contest-edit
          class="nav-link active dropdown-toggle"
          aria-haspopup="true"
          aria-expanded="false"
          >{{ activeTab }}</a
        >
        <div class="dropdown-menu">
          <a
            v-if="!virtual"
            href="#"
            data-toggle="tab"
            class="dropdown-item"
            :class="{ active: showTab === 'new_form' }"
            @click="showTab = 'new_form'"
            >{{ T.contestEdit }}</a
          >
          <a
            v-if="!virtual"
            href="#"
            data-toggle="tab"
            class="dropdown-item problems"
            :class="{ active: showTab === 'problems' }"
            @click="showTab = 'problems'"
            >{{ T.wordsAddProblem }}</a
          >
          <a
            v-if="!virtual && !details.contest_for_teams"
            href="#"
            data-toggle="tab"
            class="dropdown-item admission-mode"
            :class="{ active: showTab === 'publish' }"
            @click="showTab = 'publish'"
            >{{ T.contestNewFormAdmissionMode }}</a
          >
          <a
            v-if="!details.contest_for_teams"
            href="#"
            data-toggle="tab"
            data-nav-contestant
            class="dropdown-item contestants"
            :class="{ active: showTab === 'contestants' }"
            @click="showTab = 'contestants'"
            >{{ T.contestAdduserAddContestant }}</a
          >
          <a
            v-if="details.contest_for_teams"
            href="#"
            data-toggle="tab"
            data-nav-group
            class="dropdown-item groups"
            :class="{ active: showTab === 'groups' }"
            @click="showTab = 'groups'"
            >{{ T.contestAddgroupAddGroup }}</a
          >
          <a
            href="#"
            data-toggle="tab"
            class="dropdown-item"
            :class="{ active: showTab === 'admins' }"
            @click="showTab = 'admins'"
            >{{ T.omegaupTitleContestAddAdmin }}</a
          >
          <a
            href="#"
            data-toggle="tab"
            class="dropdown-item"
            :class="{ active: showTab === 'links' }"
            @click="showTab = 'links'"
            >{{ T.showLinks }}</a
          >
          <a
            href="#"
            data-toggle="tab"
            class="dropdown-item"
            :class="{ active: showTab === 'clone' }"
            @click="showTab = 'clone'"
            >{{ T.courseEditClone }}</a
          >
          <a
            href="#"
            data-toggle="tab"
            class="dropdown-item"
            :class="{ active: showTab === 'archive' }"
            @click="showTab = 'archive'"
            >{{ T.contestEditArchive }}</a
          >
        </div>
      </li>
    </ul>

    <div class="tab-content">
      <div v-if="showTab === 'new_form'" class="tab-pane active">
        <omegaup-contest-new-form
          :initial-alias="details.alias"
          :initial-title="details.title"
          :initial-description="details.description"
          :initial-start-time="details.start_time"
          :initial-finish-time="details.finish_time"
          :initial-window-length="details.window_length"
          :initial-points-decay-factor="details.points_decay_factor"
          :initial-submissions-gap="details.submissions_gap"
          :initial-languages="details.languages"
          :initial-feedback="details.feedback"
          :initial-penalty="details.penalty"
          :initial-scoreboard="details.scoreboard"
          :initial-penalty-type="details.penalty_type"
          :initial-show-scoreboard-after="details.show_scoreboard_after"
          :initial-partial-score="details.partial_score"
          :initial-needs-basic-information="details.needs_basic_information"
          :initial-requests-user-information="details.requests_user_information"
          :all-languages="details.available_languages"
          :teams-group-alias="teamsGroupAlias"
          :contest-for-teams="details.contest_for_teams"
          :has-submissions="details.has_submissions"
          :update="true"
          :search-result-teams-groups="searchResultTeamsGroups"
          @update-search-result-teams-groups="
            (query) => $emit('update-search-result-teams-groups', query)
          "
          @update-contest="(contest) => $emit('update-contest', contest)"
        ></omegaup-contest-new-form>
      </div>
      <div v-if="showTab === 'problems'" class="tab-pane active">
        <omegaup-contest-add-problem
          :contest-alias="details.alias"
          :initial-points="details.partial_score ? 100 : 1"
          :initial-problems="problems"
          :search-result-problems="searchResultProblems"
          @add-problem="(request) => $emit('add-problem', request)"
          @update-search-result-problems="
            (query) => $emit('update-search-result-problems', query)
          "
          @get-versions="(request) => $emit('get-versions', request)"
          @remove-problem="
            (problemAlias) => $emit('remove-problem', problemAlias)
          "
          @runs-diff="
            (problemAlias, versions, selectedCommit) =>
              $emit('runs-diff', problemAlias, versions, selectedCommit)
          "
        >
        </omegaup-contest-add-problem>
      </div>
      <div v-if="showTab === 'publish'" class="tab-pane active">
        <omegaup-common-publish
          :initial-admission-mode="details.admission_mode"
          :should-show-public-option="true"
          :admission-mode-description="T.contestAdmissionModeDescription"
          @emit-update-admission-mode="
            (admissionMode) => $emit('update-admission-mode', admissionMode)
          "
        ></omegaup-common-publish>
      </div>
      <div v-if="showTab === 'contestants'" class="tab-pane active contestants">
        <omegaup-contest-add-contestant
          :contest="details"
          :users="users"
          :search-result-users="searchResultUsers"
          @add-user="(contestants) => $emit('add-user', contestants)"
          @update-search-result-users="
            (query) => $emit('update-search-result-users', query)
          "
          @remove-user="(contestant) => $emit('remove-user', contestant)"
          @save-end-time="(user) => $emit('save-end-time', user)"
        ></omegaup-contest-add-contestant>
        <omegaup-common-requests
          :data="requests"
          :text-add-participant="T.contestAdduserAddContestant"
          @accept-request="(request) => $emit('accept-request', request)"
          @deny-request="(request) => $emit('deny-request', request)"
        ></omegaup-common-requests>
        <omegaup-contest-groups
          :groups="groups"
          :search-result-groups="searchResultGroups"
          @update-search-result-groups="
            (query) => $emit('update-search-result-groups', query)
          "
          @emit-add-group="(groupAlias) => $emit('add-group', groupAlias)"
          @emit-remove-group="(groupAlias) => $emit('remove-group', groupAlias)"
        ></omegaup-contest-groups>
      </div>
      <div v-if="showTab === 'groups'" class="tab-pane active groups">
        <omegaup-contest-teams-groups
          :teams-group="teamsGroup"
          :search-result-teams-groups="searchResultTeamsGroups"
          :has-submissions="details.has_submissions"
          @update-search-result-teams-groups="
            (query) => $emit('update-search-result-teams-groups', query)
          "
          @replace-teams-group="
            (request) => $emit('replace-teams-group', request)
          "
        ></omegaup-contest-teams-groups>
      </div>
      <div v-if="showTab === 'admins'" class="tab-pane active">
        <omegaup-contest-admins
          :admins="admins"
          :search-result-users="searchResultUsers"
          @add-admin="(username) => $emit('add-admin', username)"
          @remove-admin="(username) => $emit('remove-admin', username)"
          @update-search-result-users="
            (query) => $emit('update-search-result-users', query)
          "
        ></omegaup-contest-admins>
        <div class="mt-2"></div>
        <omegaup-contest-group-admins
          :group-admins="groupAdmins"
          @add-group-admin="
            (groupAlias) => $emit('add-group-admin', groupAlias)
          "
          @remove-group-admin="
            (groupAlias) => $emit('remove-group-admin', groupAlias)
          "
        ></omegaup-contest-group-admins>
      </div>
      <div v-if="showTab === 'links'" class="tab-pane active">
        <omegaup-contest-links :data="details"></omegaup-contest-links>
      </div>
      <div v-if="showTab === 'clone'" class="tab-pane active">
        <omegaup-contest-clone
          @clone="
            ({ title, alias, description, startTime }) =>
              $emit('clone-contest', title, alias, description, startTime)
          "
        ></omegaup-contest-clone>
      </div>
      <div v-if="showTab === 'archive'" class="tab-pane active">
        <omegaup-common-archive
          :already-archived="alreadyArchived"
          :archive-button-description="archiveButtonDescription"
          :archive-confirm-text="T.contestEditArchiveConfirmText"
          :archive-header-title="T.contestEditArchiveContest"
          :archive-help-text="archiveUnarchiveDescription"
          @archive="onArchiveContest"
        ></omegaup-common-archive>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator';
import { types } from '../../api_types';
import T from '../../lang';
import * as ui from '../../ui';

import contest_AddProblem from './AddProblem.vue';
import contest_AddContestant from './AddContestant.vue';
import contest_Clone from './Clone.vue';
import contest_Admins from '../common/Adminsv2.vue';
import common_Archive from '../common/Archive.vue';
import common_Requests from '../common/Requests.vue';
import contest_GroupAdmins from '../common/GroupAdminsv2.vue';
import contest_Groups from './Groups.vue';
import contest_TeamsGroups from './TeamsGroup.vue';
import contest_Links from './Links.vue';
import contest_NewForm from './NewForm.vue';
import common_Publish from '../common/Publishv2.vue';

@Component({
  components: {
    'omegaup-contest-add-problem': contest_AddProblem,
    'omegaup-contest-admins': contest_Admins,
    'omegaup-contest-clone': contest_Clone,
    'omegaup-contest-add-contestant': contest_AddContestant,
    'omegaup-common-archive': common_Archive,
    'omegaup-common-requests': common_Requests,
    'omegaup-contest-groups': contest_Groups,
    'omegaup-contest-teams-groups': contest_TeamsGroups,
    'omegaup-contest-group-admins': contest_GroupAdmins,
    'omegaup-contest-links': contest_Links,
    'omegaup-contest-new-form': contest_NewForm,
    'omegaup-common-publish': common_Publish,
  },
})
export default class Edit extends Vue {
  @Prop() admins!: types.ContestAdmin[];
  @Prop() details!: types.ContestAdminDetails;
  @Prop() groups!: types.ContestGroup[];
  @Prop() groupAdmins!: types.ContestGroupAdmin[];
  @Prop() problems!: types.ProblemsetProblemWithVersions[];
  @Prop() requests!: types.ContestRequest[];
  @Prop() users!: types.ContestUser[];
  @Prop() searchResultProblems!: types.ListItem[];
  @Prop() searchResultUsers!: types.ListItem[];
  @Prop() teamsGroup!: types.ContestGroup | null;
  @Prop() searchResultTeamsGroups!: types.ListItem[];
  @Prop() searchResultGroups!: types.ListItem[];

  T = T;
  ui = ui;
  showTab = ui.isVirtual(this.details) ? 'contestants' : 'new_form';
  virtual = ui.isVirtual(this.details);
  alreadyArchived = this.details.archived;

  get activeTab(): string {
    switch (this.showTab) {
      case 'new_form':
        return T.contestEdit;
      case 'problems':
        return T.wordsAddProblem;
      case 'publish':
        return T.contestNewFormAdmissionMode;
      case 'contestants':
        return T.contestAdduserAddContestant;
      case 'groups':
        return T.contestAddgroupAddGroup;
      case 'admins':
        return T.omegaupTitleContestAddAdmin;
      case 'links':
        return T.showLinks;
      case 'clone':
        return T.courseEditClone;
      case 'archive':
        return T.contestEditArchive;
      default:
        return T.contestEdit;
    }
  }

  get archiveButtonDescription(): string {
    if (this.alreadyArchived) {
      return T.contestEditUnarchiveContest;
    }
    return T.contestEditArchiveContest;
  }

  get archiveUnarchiveDescription(): string {
    if (this.alreadyArchived) {
      return T.contestEditUnarchiveHelpText;
    }
    return T.contestEditArchiveHelpText;
  }

  get teamsGroupAlias(): null | string {
    return this.teamsGroup?.alias ?? null;
  }

  onArchiveContest(archive: boolean): void {
    this.$emit('archive-contest', this.details.alias, archive);
    this.alreadyArchived = archive;
  }
}
</script>
