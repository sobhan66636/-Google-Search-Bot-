<template>
  <v-container>
    <v-card>
      <v-card-title>
        Best Suggestions Search
      </v-card-title>
      <v-card-text>
        <v-alert
          v-if="error"
          type="error"
          dismissible
        >
          {{ error }}
        </v-alert>
  
        <!-- Search Input -->
        <v-text-field
          v-model="searchQuery"
          label="Search Suggestions"
          outlined
          clearable
          class="mb-4"
          @input="filterSuggestions"
        />
  
        <!-- Suggestions Table -->
        <v-data-table
          :headers="headers"
          :items="filteredSuggestions"
          class="elevation-1"
          no-data-text="No suggestions found."
        >
          <template #top>
            <v-toolbar flat>
              <v-toolbar-title>Suggestions</v-toolbar-title>
              <v-spacer />
              <v-btn
                color="primary"
                @click="fetchResults"
              >
                Refresh Data
              </v-btn>
            </v-toolbar>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </v-container>
</template>
  
  <script setup>
  import { ref, onMounted } from "vue";
  import axios from "axios";
  
  // Table Headers
  const headers = [
    { text: "Keyword", value: "keyword" },
    { text: "Suggestions", value: "suggestion" },
  ];
  
  // Data and States
  const allSuggestions = ref([]); // Holds all combined suggestions
  const filteredSuggestions = ref([]); // Suggestions filtered by search
  const searchQuery = ref(""); // User's search input
  const error = ref(null);
  
  // Fetch API Data
  const fetchResults = async () => {
    try {
      error.value = null;
  
      // Fetch data from the API
      const response = await axios.get("http://localhost:5000/results");
  
      // Combine suggestions across all keywords
      const suggestionsMap = new Map();
      response.data.results.forEach((result) => {
        result.suggestions.forEach((suggestion) => {
          if (!suggestionsMap.has(suggestion)) {
            suggestionsMap.set(suggestion, {
              keyword: result.keyword,
              suggestion: suggestion,
            });
          }
        });
      });
  
      // Store suggestions as an array
      allSuggestions.value = Array.from(suggestionsMap.values());
      filteredSuggestions.value = allSuggestions.value; // Initially show all
    } catch (err) {
      error.value = "Failed to fetch data from API.";
      console.error(err);
    }
  };
  
  // Filter Suggestions Based on Search Query
  const filterSuggestions = () => {
    if (searchQuery.value) {
      filteredSuggestions.value = allSuggestions.value.filter((item) =>
        item.suggestion.toLowerCase().includes(searchQuery.value.toLowerCase())
      );
    } else {
      filteredSuggestions.value = allSuggestions.value; // Reset when query is empty
    }
  };
  
  // Fetch data when the component mounts
  onMounted(() => {
    fetchResults();
  });
  </script>
  
  <style scoped>
  .v-data-table__wrapper {
    max-height: 400px;
    overflow-y: auto;
  }
  </style>
  