<template>
  <div class="card">
    <div v-if="!update" class="card-header bg-primary text-white panel-heading">
      <h3 class="card-title mb-0">{{ T.contestNew }}</h3>
    </div>
    <div class="card-body">
      <div class="btn-group d-block mb-3 text-center">
        <button class="btn btn-secondary" data-contest-omi @click="fillOmi">
          {{ T.contestNewFormOmiStyle }}
        </button>
        <button
          class="btn btn-secondary"
          data-contest-preioi
          @click="fillPreIoi"
        >
          {{ T.contestNewForm }}
        </button>
        <button
          class="btn btn-secondary"
          data-contest-conacup
          @click="fillConacup"
        >
          {{ T.contestNewFormConacupStyle }}
        </button>
        <button class="btn btn-secondary" data-contest-cpc @click="fillIcpc">
          {{ T.contestNewFormICPCStyle }}
        </button>
      </div>
      <form class="contest-form" @submit.prevent="onSubmit">
        <div class="row">
          <div class="form-group col-md-6">
            <label>{{ T.wordsTitle }}</label>
            <input
              v-model="title"
              class="form-control"
              :class="{
                'is-invalid': invalidParameterName === 'title',
              }"
              name="title"
              data-title
              :placeholder="titlePlaceHolder"
              size="30"
              type="text"
              required="required"
            />
          </div>
          <div class="form-group col-md-6">
            <label>{{ T.contestNewFormShortTitleAlias }}</label>
            <input
              v-model="alias"
              class="form-control"
              :class="{
                'is-invalid': invalidParameterName === 'alias',
              }"
              name="alias"
              :disabled="update"
              type="text"
              required="required"
            />
            <p class="help-block">
              {{ T.contestNewFormShortTitleAliasDesc }}
            </p>
          </div>
        </div>
        <div class="row">
          <div class="form-group col-md-6">
            <label>{{ T.contestNewFormStartDate }}</label>
            <omegaup-datetimepicker
              v-model="startTime"
            ></omegaup-datetimepicker>
            <p class="help-block">{{ T.contestNewFormStartDateDesc }}</p>
          </div>
          <div class="form-group col-md-6">
            <label>{{ T.contestNewFormEndDate }}</label>
            <omegaup-datetimepicker
              v-model="finishTime"
              :is-invalid="invalidParameterName === 'finish_time'"
            ></omegaup-datetimepicker>
            <p class="help-block">{{ T.contestNewFormEndDateDesc }}</p>
          </div>
        </div>
        <div class="row">
          <div class="form-group col-md-6">
            <label>{{ T.contestNewFormDescription }}</label>
            <textarea
              v-model="description"
              class="form-control"
              :class="{
                'is-invalid': invalidParameterName === 'description',
              }"
              name="description"
              cols="30"
              rows="10"
              required="required"
            ></textarea>
          </div>
          <div class="form-group col-md-6">
            <label>{{ T.contestNewFormDifferentStarts }}</label>
            <div class="checkbox">
              <label
                ><input v-model="windowLengthEnabled" type="checkbox" />
                {{ T.wordsEnable }}</label
              >
            </div>
            <input
              v-model="windowLength"
              class="form-control"
              :class="{
                'is-invalid': invalidParameterName === 'window_length',
              }"
              size="3"
              type="text"
              :disabled="!windowLengthEnabled"
            />
            <p class="help-block">{{ T.contestNewFormDifferentStartsDesc }}</p>
          </div>
        </div>
        <div class="row">
          <div class="form-group col-md-6">
            <label>{{ T.contestNewFormScoreboardTimePercent }}</label>
            <input
              v-model="scoreboard"
              class="form-control scoreboard-time-percent"
              :class="{
                'is-invalid': invalidParameterName === 'scoreboard',
              }"
              name="scoreboard"
              size="3"
              type="text"
              required="required"
            />
            <p class="help-block">
              {{ T.contestNewFormScoreboardTimePercentDesc }}
            </p>
          </div>
          <div class="form-group col-md-6">
            <label>{{ T.contestNewFormSubmissionsSeparation }}</label>
            <input
              v-model="submissionsGap"
              class="form-control"
              :class="{
                'is-invalid': invalidParameterName === 'submissions_gap',
              }"
              size="2"
              type="text"
              required="required"
            />
            <p class="help-block">
              {{ T.contestNewFormSubmissionsSeparationDesc }}
            </p>
          </div>
        </div>
        <div class="row">
          <div class="form-group col-md-6">
            <label>{{ T.contestNewFormPenaltyType }}</label>
            <select v-model="penaltyType" class="form-control">
              <option value="none">
                {{ T.contestNewFormNoPenalty }}
              </option>
              <option value="problem_open">
                {{ T.contestNewFormByProblem }}
              </option>
              <option value="contest_start">
                {{ T.contestNewFormByContests }}
              </option>
              <option value="runtime">
                {{ T.contestNewFormByRuntime }}
              </option>
            </select>
            <p class="help-block">{{ T.contestNewFormPenaltyTypeDesc }}</p>
          </div>
          <div class="form-group col-md-6">
            <label>{{ T.wordsPenalty }}</label>
            <input
              v-model="penalty"
              class="form-control"
              :class="{
                'is-invalid': invalidParameterName === 'penalty',
              }"
              size="2"
              type="text"
              required="required"
            />
            <p class="help-block">{{ T.contestNewFormPenaltyDesc }}</p>
          </div>
        </div>
        <div class="row">
          <div class="form-group col-md-4">
            <label>{{ T.wordsFeedback }}</label>
            <select v-model="feedback" class="form-control">
              <option value="none">
                {{ T.wordsNone }}
              </option>
              <option value="summary">
                {{ T.wordsSummary }}
              </option>
              <option value="detailed">
                {{ T.wordsDetailed }}
              </option>
            </select>
            <p class="help-block">
              {{ T.contestNewFormImmediateFeedbackDesc }}
            </p>
          </div>
          <div class="form-group col-md-4">
            <label>{{ T.contestNewFormScoreboardAtEnd }}</label>
            <select v-model="showScoreboardAfter" class="form-control">
              <option :value="true">
                {{ T.wordsYes }}
              </option>
              <option :value="false">
                {{ T.wordsNo }}
              </option>
            </select>
            <p class="help-block">{{ T.contestNewFormScoreboardAtEndDesc }}</p>
          </div>
          <div class="form-group col-md-4">
            <label>{{ T.contestNewFormPartialScore }}</label>
            <select v-model="partialScore" class="form-control">
              <option :value="true">
                {{ T.wordsYes }}
              </option>
              <option :value="false">
                {{ T.wordsNo }}
              </option>
            </select>
            <p class="help-block">{{ T.contestNewFormPartialScoreDesc }}</p>
          </div>
        </div>
        <div class="row">
          <div class="form-group col-md-6">
            <label>{{ T.contestNewFormPointDecrementFactor }}</label>
            <input
              v-model="pointsDecayFactor"
              class="form-control"
              :class="{
                'is-invalid': invalidParameterName === 'points_decay_factor',
              }"
              size="4"
              type="text"
              required="required"
            />
            <p class="help-block">
              {{ T.contestNewFormPointDecrementFactorDesc }}
            </p>
          </div>
          <div class="form-group col-md-6">
            <label>{{ T.wordsLanguages }}</label
            ><br />
            <multiselect
              v-model="languages"
              :options="Object.keys(allLanguages)"
              :multiple="true"
              :placeholder="T.contestNewFormLanguages"
              :close-on-select="false"
              :allow-empty="false"
            >
            </multiselect>
            <p class="help-block">{{ T.contestNewFormLanguages }}</p>
          </div>
        </div>
        <div class="row">
          <div class="form-group col-md-6">
            <label>{{ T.contestNewFormBasicInformationRequired }}</label>
            <div class="checkbox">
              <label
                ><input v-model="needsBasicInformation" type="checkbox" />{{
                  T.wordsEnable
                }}</label
              >
            </div>
            <p class="help-block">
              {{ T.contestNewFormBasicInformationRequiredDesc }}
            </p>
          </div>
          <div class="form-group col-md-6">
            <label>{{ T.contestNewFormUserInformationRequired }}</label>
            <select v-model="requestsUserInformation" class="form-control">
              <option value="no">
                {{ T.wordsNo }}
              </option>
              <option value="optional">
                {{ T.wordsOptional }}
              </option>
              <option value="required">
                {{ T.wordsRequired }}
              </option>
            </select>
            <p class="help-block">
              {{ T.contestNewFormUserInformationRequiredDesc }}
            </p>
          </div>
        </div>
        <div class="form-group">
          <button class="btn btn-primary" type="submit">
            {{
              update
                ? T.contestNewFormUpdateContest
                : T.contestNewFormScheduleContest
            }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import { Vue, Component, Prop, Watch } from 'vue-property-decorator';
import T from '../../lang';
import common_Typeahead from '../common/Typeahead.vue';
import DateTimePicker from '../DateTimePicker.vue';
import Multiselect from 'vue-multiselect';
import { types } from '../../api_types';

@Component({
  components: {
    'omegaup-common-typeahead': common_Typeahead,
    'omegaup-datetimepicker': DateTimePicker,
    Multiselect,
  },
})
export default class NewForm extends Vue {
  @Prop() update!: boolean;
  @Prop() allLanguages!: string[];
  @Prop({ default: '' }) initialAlias!: string;
  @Prop({ default: '' }) initialDescription!: string;
  @Prop({ default: 'none' }) initialFeedback!: string;
  @Prop() initialLanguages!: string[];
  @Prop() initialFinishTime!: Date;
  @Prop({ default: false }) initialNeedsBasicInformation!: boolean;
  @Prop({ default: 0 }) initialPenalty!: number;
  @Prop({ default: 'none' }) initialPenaltyType!: string;
  @Prop({ default: 0.0 }) initialPointsDecayFactor!: number;
  @Prop({ default: 'no' }) initialRequestsUserInformation!: string;
  @Prop({ default: 100 }) initialScoreboard!: number;
  @Prop({ default: true }) initialShowScoreboardAfter!: boolean;
  @Prop({ default: true }) initialPartialScore!: boolean;
  @Prop({ default: false }) hasSubmissions!: boolean;
  @Prop() initialStartTime!: Date;
  @Prop() initialSubmissionsGap!: number;
  @Prop({ default: '' }) initialTitle!: string;
  @Prop({ default: null }) initialWindowLength!: null | number;
  @Prop({ default: null }) invalidParameterName!: null | string;
  @Prop({ default: null }) teamsGroupAlias!: null | string;
  @Prop() searchResultTeamsGroups!: types.ListItem[];
  @Prop({ default: false }) contestForTeams!: boolean;

  T = T;
  alias = this.initialAlias;
  description = this.initialDescription;
  feedback = this.initialFeedback;
  finishTime = this.initialFinishTime;
  languages = this.initialLanguages;
  needsBasicInformation = this.initialNeedsBasicInformation;
  penalty = this.initialPenalty;
  penaltyType = this.initialPenaltyType;
  pointsDecayFactor = this.initialPointsDecayFactor;
  requestsUserInformation = this.initialRequestsUserInformation;
  scoreboard = this.initialScoreboard;
  showScoreboardAfter = this.initialShowScoreboardAfter;
  partialScore = this.initialPartialScore;
  startTime = this.initialStartTime;
  submissionsGap = this.initialSubmissionsGap
    ? this.initialSubmissionsGap / 60
    : 1;
  title = this.initialTitle;
  windowLength = this.initialWindowLength;
  windowLengthEnabled = this.initialWindowLength !== null;
  currentContestForTeams = this.contestForTeams;
  currentTeamsGroupAlias = this.teamsGroupAlias;
  titlePlaceHolder = '';

  @Watch('windowLengthEnabled')
  onPropertyChange(newValue: boolean): void {
    if (!newValue) {
      this.windowLength = null;
    }
  }

  fillOmi(): void {
    this.languages = Object.keys(this.allLanguages);
    this.titlePlaceHolder = T.contestNewFormTitlePlaceholderOmiStyle;
    this.windowLengthEnabled = false;
    this.windowLength = 0;
    this.scoreboard = 0;
    this.pointsDecayFactor = 0;
    this.submissionsGap = 1;
    this.feedback = 'detailed';
    this.penalty = 0;
    this.penaltyType = 'none';
    this.showScoreboardAfter = true;
    this.partialScore = true;
  }

  fillPreIoi(): void {
    this.languages = Object.keys(this.allLanguages);
    this.titlePlaceHolder = T.contestNewFormTitlePlaceholderIoiStyle;
    this.windowLengthEnabled = true;
    this.windowLength = 180;
    this.scoreboard = 0;
    this.pointsDecayFactor = 0;
    this.submissionsGap = 0;
    this.feedback = 'detailed';
    this.penalty = 0;
    this.penaltyType = 'none';
    this.showScoreboardAfter = true;
    this.partialScore = true;
  }

  fillConacup(): void {
    this.languages = Object.keys(this.allLanguages);
    this.titlePlaceHolder = T.contestNewFormTitlePlaceholderConacupStyle;
    this.windowLengthEnabled = false;
    this.windowLength = 0;
    this.scoreboard = 75;
    this.pointsDecayFactor = 0;
    this.submissionsGap = 1;
    this.feedback = 'detailed';
    this.penalty = 20;
    this.penaltyType = 'none';
    this.showScoreboardAfter = true;
    this.partialScore = true;
  }

  fillIcpc(): void {
    const languagesKeys = Object.keys(this.allLanguages);
    this.languages = languagesKeys.filter(
      (lang) =>
        lang.includes('c11') ||
        lang.includes('cpp') ||
        lang.includes('py') ||
        lang.includes('java'),
    );
    this.titlePlaceHolder = T.contestNewFormTitlePlaceholderICPCStyle;
    this.windowLengthEnabled = false;
    this.windowLength = null;
    this.scoreboard = 80;
    this.pointsDecayFactor = 0;
    this.submissionsGap = 1;
    this.feedback = 'none';
    this.penalty = 20;
    this.penaltyType = 'contest_start';
    this.showScoreboardAfter = true;
    this.partialScore = false;
  }

  onSubmit() {
    const contest: types.ContestAdminDetails = {
      admin: true,
      admission_mode: 'private',
      alias: this.alias,
      archived: false,
      available_languages: {},
      director: '',
      opened: false,
      penalty_calc_policy: 'sum',
      problemset_id: 0,
      show_penalty: true,
      title: this.title,
      description: this.description,
      has_submissions: this.hasSubmissions,
      start_time: this.startTime,
      finish_time: this.finishTime,
      points_decay_factor: this.pointsDecayFactor,
      submissions_gap: (this.submissionsGap || 1) * 60,
      languages: this.languages,
      feedback: this.feedback,
      penalty: this.penalty,
      scoreboard: this.scoreboard,
      penalty_type: this.penaltyType,
      show_scoreboard_after: this.showScoreboardAfter,
      partial_score: this.partialScore,
      needs_basic_information: this.needsBasicInformation,
      requests_user_information: this.requestsUserInformation,
      contest_for_teams: this.currentContestForTeams,
    };
    if (this.windowLengthEnabled && this.windowLength) {
      contest.window_length = this.windowLength;
    }
    const request = { contest, teamsGroupAlias: this.currentTeamsGroupAlias };
    if (this.update) {
      this.$emit('update-contest', request);
      return;
    }
    this.$emit('create-contest', request);
  }
}
</script>

<style lang="scss" scoped>
@import '../../../../sass/main.scss';
@import '../../../../../../node_modules/vue-multiselect/dist/vue-multiselect.min.css';

.multiselect__tag {
  background: var(--multiselect-tag-background-color);
}
</style>
