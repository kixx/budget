<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Budget</h1>
        <hr>
          <alert :message="message" v-if="showMessage"></alert>
          <b-button id="add-budget" variant="success" size="sm"
             v-b-modal.budget-modal>Add Budget Line</b-button>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">Date</th>
              <th scope="col">Budget</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!budget.length" id="no-data"><td colspan="3">No data</td></tr>
            <tr v-for="(item, index) in budget" :key="index">
                <td>{{ item.datetime }}</td>
                <td>{{ item.budget }}</td>
                <td>
                  <b-button-group size="sm">
                      <b-button
                            type="button"
                            variant="warning"
                            v-b-modal.budget-update-modal
                            @click="editBudget(item)">
                        Update
                      </b-button>
                      <b-button
                            type="button"
                            variant="danger"
                            @click="onDeleteItem(item)">
                        Delete
                      </b-button>
                  </b-button-group>
                </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <b-modal ref="addBudgetModal"
            id="budget-modal"
            title="Add a new budget line"
            hide-footer>
    <b-form @submit="onSubmit" @reset="onReset" class="w-100">
    <b-form-group id="form-datetime-group"
                    label="Datetime:"
                    label-for="form-datetime-input">
        <date-picker id="form-datetime-input"
                        v-model="addBudgetForm.datetime"
                        required
                        placeholder="Enter datetime"
                        type="datetime"
                        value-type="format"
                        :format="format"
                        :lang="lang">
        </date-picker>
        </b-form-group>
        <b-form-group id="form-budget-group"
                    label="Budget:"
                    label-for="form-budget-input">
            <b-form-input id="form-budget-input"
                        type="text"
                        v-model="addBudgetForm.budget"
                        required
                        placeholder="Enter budget">
            </b-form-input>
        </b-form-group>
        <b-button-group>
        <b-button type="submit" variant="primary">Submit</b-button>
        <b-button type="reset" variant="danger">Reset</b-button>
        </b-button-group>
    </b-form>
    </b-modal>
    <b-modal ref="editBudgetModal"
            id="budget-update-modal"
            title="Update"
            hide-footer>
    <b-form @submit="onSubmitUpdate" @reset="onResetUpdate" class="w-100">
    <b-form-group id="form-datetime-edit-group"
                    label="Datetime:"
                    label-for="form-datetime-edit-input">
        <date-picker id="form-datetime-edit-input"
                        v-model="editForm.datetime"
                        required
                        placeholder="Enter datetime"
                        type="datetime"
                        value-type="format"
                        :format="format"
                        :lang="lang">
        </date-picker>
        </b-form-group>
        <b-form-group id="form-budget-edit-group"
                    label="Budget:"
                    label-for="form-budget-edit-input">
            <b-form-input id="form-budget-edit-input"
                        type="text"
                        v-model="editForm.budget"
                        required
                        placeholder="Enter budget">
            </b-form-input>
        </b-form-group>
        <b-button-group>
        <b-button type="submit" variant="primary">Update</b-button>
        <b-button type="reset" variant="danger">Cancel</b-button>
        </b-button-group>
    </b-form>
    </b-modal>
  </div>
</template>
<style>
button#add-budget {
  margin-bottom: 15px;
}
</style>
<script>
import axios from 'axios';
import DatePicker from 'vue2-datepicker';
import Alert from './Alert.vue';

export default {
  data() {
    return {
      budget: [],
      addBudgetForm: {
        datetime: '',
        budget: '',
      },
      editForm: {
        datetime: '',
        budget: '',
      },
      message: '',
      showMessage: false,
      item: null,
      lang: 'en',
      format: 'MM.DD.YYYY hh:mm:ss',
    };
  },
  components: {
    alert: Alert,
    DatePicker,
  },
  methods: {
    loadBudget() {
      const path = 'http://94.130.179.105:5000/api/budget';
      axios.get(path)
        .then((res) => {
          this.budget = res.data.budget;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);        
        });
    },
    addBudget(payload) {
      const path = 'http://94.130.179.105:5000/api/budget';
      axios.post(path, payload)
        .then(() => {
          this.loadBudget();
          this.message = 'Budget line added!';
          this.showMessage = true;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
          this.loadBudget();
          this.showMessage = false;
        });
    },
    updateBudget(payload, id) {
      const path = `http://94.130.179.105:5000/api/budget/${id}`;
      axios.put(path, payload)
        .then(() => {
          this.loadBudget();
          this.message = 'Budget updated!';
          this.showMessage = true;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loadBudget();
        });
    },
    editBudget(item) {
      this.editForm = item;
    },
    removeBudget(id) {
      const path = `http://94.130.179.105:5000/api/budget/${id}`;
      axios.delete(path)
        .then(() => {
          this.loadBudget();
          this.message = 'Budget line removed!';
          this.showMessage = true;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loadBudget();
        });
    },
    onDeleteItem(item) {
      this.removeBudget(item.id);
    },
    initForm() {
      this.addBudgetForm.datetime = '';
      this.addBudgetForm.budget = '';
      this.editForm.id = '';
      this.editForm.datetime = '';
      this.editForm.budget = '';
    },
    onSubmit(evt) {
      evt.preventDefault();
      this.$refs.addBudgetModal.hide();
      const payload = {
        datetime: this.addBudgetForm.datetime,
        budget: this.addBudgetForm.budget,
      };
      this.addBudget(payload);
      this.initForm();
    },
    onReset(evt) {
      evt.preventDefault();
      this.$refs.addBudgetModal.hide();
      this.initForm();
      this.loadBudget();
    },
    onSubmitUpdate(evt) {
      evt.preventDefault();
      this.$refs.editBudgetModal.hide();
      const payload = {
        datetime: this.editForm.datetime,
        budget: this.editForm.budget,
      };
      this.updateBudget(payload, this.editForm.id);
    },
    onResetUpdate(evt) {
      evt.preventDefault();
      this.$refs.editBudgetModal.hide();
      this.initForm();
      this.loadBudget();
    },
  },
  created() {
    this.loadBudget();
  },
};
</script>
