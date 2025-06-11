<template>
  <v-card>
    <v-card-title>Manage Websites</v-card-title>
    <v-card-text>
      <!-- Form to Add or Edit Website -->
      <v-form @submit.prevent="submitWebsite">
        <v-text-field
          v-model="currentWebsite.name"
          label="Website Name"
          required
          dense
          outlined
        />

        <v-text-field
          v-model="currentWebsite.domain"
          label="Website Domain"
          required
          dense
          outlined
        />

        <v-btn
          type="submit"
          color="primary"
          class="mt-4"
          :disabled="isLoading"
        >
          {{ isEditMode ? "Update Website" : "Add Website" }}
        </v-btn>
      </v-form>

      <v-divider class="my-4" />

      <div v-if="isLoading">
        <v-progress-circular
          indeterminate
          color="primary"
        />
      </div>

      <div v-if="websites.length && !isLoading">
        <!-- Scrollable list of websites -->
        <div class="scrollable-list">
          <v-list dense>
            <v-list-item
              v-for="website in websites"
              :key="website.id"
              class="mb-2"
            >
              <hr>
              <br>
              <v-list-item-content>
                <v-list-item-title>{{ website.name }}</v-list-item-title>
                <span>Website Domain: {{ website.domain }}</span>
              </v-list-item-content>
              <v-list-item-action>
                <v-btn
                  color="blue"
                  @click="editWebsite(website)"
                >
                  Edit
                </v-btn>
                <v-btn
                  color="red"
                  :disabled="isLoading"
                  @click="deleteWebsite(website.id)"
                >
                  Delete
                </v-btn>
              </v-list-item-action>
            </v-list-item>
          </v-list>
        </div>
      </div>


      <v-alert
        v-else
        type="info"
        outlined
      >
        No websites available.
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const websites = ref([]);
const currentWebsite = ref({ id: null, name: "", domain: "" });
const isLoading = ref(false);
const isEditMode = ref(false); // Track if we're editing a website

const fetchWebsites = async () => {
  isLoading.value = true;
  try {
    const response = await axios.get("http://localhost:5000/websites");
    websites.value = response.data;
  } catch (error) {
    console.error("Error fetching websites:", error);
  } finally {
    isLoading.value = false;
  }
};

const submitWebsite = async () => {
  isLoading.value = true;
  try {
    if (isEditMode.value) {
      // Update website
      await axios.put("http://localhost:5000/websites", currentWebsite.value);
      const index = websites.value.findIndex(
        (website) => website.id === currentWebsite.value.id
      );
      websites.value[index] = currentWebsite.value; // Update in the list
    } else {
      // Add new website
      const response = await axios.post("http://localhost:5000/websites", currentWebsite.value);
      websites.value.push(response.data.website); // Add to the list
    }
    location.reload();
    currentWebsite.value = { id: null, name: "", domain: "" }; // Clear form
    isEditMode.value = false; // Reset edit mode

  } catch (error) {
    console.error("Error submitting website:", error);
  } finally {
    isLoading.value = false;
  }
};

const deleteWebsite = async (id) => {
  isLoading.value = true;
  try {
    await axios.delete("http://localhost:5000/websites", { data: { id } });
    websites.value = websites.value.filter((website) => website.id !== id);
    location.reload();
  } catch (error) {
    console.error("Error deleting website:", error);
  } finally {
    isLoading.value = false;
  }
};

const editWebsite = (website) => {
  currentWebsite.value = { ...website }; // Copy website data into form
  isEditMode.value = true; // Switch to edit mode
};

onMounted(() => {
  fetchWebsites();
});
</script>

<style scoped>
.scrollable-list {
  max-height: 300px;
  overflow-y: auto;
}

.website-details {
  margin-top: 10px;
  padding: 10px;
  border-radius: 4px;
}
</style>
