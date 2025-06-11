<template>
  <v-card>
    <v-card-title>Manage Keywords</v-card-title>
    <v-card-text>
      <!-- Add or Edit Keyword Form -->
      <v-form @submit.prevent="submitKeyword">
        <v-text-field
          v-model="newKeyword.keyword"
          label="Keyword"
          required
          dense
          outlined
        />

        <!-- Select Associated Websites -->
        <v-select
          v-model="newKeyword.websiteIds"
          label="Associated Websites"
          :items="websites"
          item-value="id"
          item-text="title"
          multiple
          dense
          outlined
        />

        <v-btn
          type="submit"
          color="primary"
          class="mt-4"
          :disabled="isLoading"
        >
          {{ isEditMode ? "Update Keyword" : "Add Keyword" }}
        </v-btn>
      </v-form>

      <v-divider class="my-4" />

      <!-- Display List of Keywords -->
      <div v-if="isLoading">
        <v-progress-circular
          indeterminate
          color="primary"
        />
      </div>

      <div v-if="keywords.length && !isLoading">
        <v-list
          dense
          style="max-height: 300px; overflow-y: auto;"
        >
          <v-list-item
            v-for="keyword in keywords"
            :key="keyword.id"
            class="mb-2"
          >
            <hr>
            <br>
            <v-list-item-content>
              <v-list-item-title>
                {{ keyword.keyword }}
              </v-list-item-title>

              <!-- Associated Websites with layout improvements -->
              <v-list-item-subtitle>
                <span>Associated Websites:</span>
                <v-chip
                  v-for="website in keyword.websites"
                  :key="website.id"
                  color="blue"
                  text-color="white"
                  class="mr-2 mb-1"
                  small
                >
                  {{ website.name }}
                </v-chip>
              </v-list-item-subtitle>
            </v-list-item-content>

            <v-list-item-action>
              <!-- Edit Button -->
              <v-btn
                color="blue"
                :disabled="isLoading"
                @click="editKeyword(keyword)"
              >
                Edit
              </v-btn>

              <!-- Delete Button -->
              <v-btn
                color="red"
                :disabled="isLoading"
                @click="deleteKeyword(keyword.id)"
              >
                Delete
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-list>
      </div>

      <!-- Alert if no keywords are available -->
      <v-alert
        v-else
        type="info"
        outlined
      >
        No keywords available.
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const websites = ref([]); // List of websites
const keywords = ref([]); // List of keywords
const newKeyword = ref({
  keyword: "",
  websiteIds: [], // Holds the IDs of selected websites
});

const isLoading = ref(false);
const isEditMode = ref(false); // To track if we are editing a keyword
let currentKeywordId = ref(null); // To hold the ID of the keyword being edited

// Fetch websites from API
const fetchWebsites = async () => {
  try {
    const response = await axios.get("http://localhost:5000/websites");
    websites.value = response.data.map(website => ({
      id: website.id,
      title: website.title || website.name, // Assuming `title` or `name` field contains the website title
    }));
  } catch (error) {
    console.error("Error fetching websites:", error);
  }
};

// Fetch keywords from API
const fetchKeywords = async () => {
  try {
    const response = await axios.get("http://localhost:5000/keywords");
    keywords.value = response.data;
  } catch (error) {
    console.error("Error fetching keywords:", error);
  }
};

// Submit a new or edited keyword
const submitKeyword = async () => {
  isLoading.value = true;

  try {
    if (isEditMode.value) {
      // Update the keyword
      await axios.put(`http://localhost:5000/keywords/${currentKeywordId.value}`, {
        keyword: newKeyword.value.keyword,
        website_ids: newKeyword.value.websiteIds,
      });

      // Update the keyword in the local list
      const index = keywords.value.findIndex(k => k.id === currentKeywordId.value);
      if (index !== -1) {
        keywords.value[index] = {
          ...keywords.value[index],
          keyword: newKeyword.value.keyword,
          websites: websites.value.filter(website => newKeyword.value.websiteIds.includes(website.id)),
        };
      }
    } else {
      // Add new keyword
      const response = await axios.post("http://localhost:5000/keywords", {
        keyword: newKeyword.value.keyword,
        website_ids: newKeyword.value.websiteIds,
      });
      keywords.value.push(response.data.keyword);
    }
    location.reload();
    // Reset form
    newKeyword.value = { keyword: "", websiteIds: [] };
    isEditMode.value = false;
    currentKeywordId.value = null;
  } catch (error) {
    console.error("Error submitting keyword:", error);
  } finally {
    isLoading.value = false;
  }
};

// Edit an existing keyword
const editKeyword = (keyword) => {
  newKeyword.value.keyword = keyword.keyword;
  newKeyword.value.websiteIds = keyword.websites.map(website => website.id);
  currentKeywordId.value = keyword.id;
  isEditMode.value = true;
};

// Delete a keyword
const deleteKeyword = async (id) => {
  isLoading.value = true;
  try {
    // Send delete request for the specific keyword by id
    await axios.delete("http://localhost:5000/keywords", { data: { id } });

    // Remove the keyword from the local list
    keywords.value = keywords.value.filter((keyword) => keyword.id !== id);
    location.reload();
  } catch (error) {
    console.error("Error deleting keyword:", error);
  } finally {
    isLoading.value = false;
  }
};

// Fetch data on mounted
onMounted(() => {
  fetchWebsites();
  fetchKeywords();
});
</script>

<style scoped>
/* Style for scrollable keyword list */
.v-list {
  max-height: 300px;
  overflow-y: auto;
}

/* Custom styling for chips */
.v-chip {
  margin-right: 5px;
  margin-bottom: 5px;
}
</style>
