<template>
  <v-app-bar
    app
    color="primary"
    dark
  >
    <!-- Title on the left -->
    <v-toolbar-title>Website and Keyword Manager</v-toolbar-title>
    
    <!-- Spacer to push badges to the center -->
    <v-spacer />
    
    <!-- Container for the badges (centered in the header) -->
    <div class="d-flex justify-center align-center flex-grow-1">
      <!-- API Status (Larger with space) -->
      <v-badge
        v-if="apiStatus === 'online'"
        color="success"
        content="API Online"
        class="badge-status"
      />
      <v-badge
        v-else
        color="error"
        content="API Offline"
        class="badge-status"
      />

      <!-- Bot Status (Larger with space) -->
      <v-badge
        v-if="botStatus === 'online'"
        color="success"
        content="Bot Online"
        class="badge-status"
      />
      <v-badge
        v-else
        color="error"
        content="Bot Offline"
        class="badge-status"
      />
    </div>
  </v-app-bar>
</template>

<script setup>
import { ref , onMounted, onUnmounted } from 'vue';
import axios from 'axios';
const logs = ref([]);
const lastLog = ref(null);
const timeDifference = ref(null);
const currentTime = ref(new Date());
// Reactive variables for API and bot status
const apiStatus = ref('checking'); // Default status: checking
const botStatus = ref('checking'); // Default status: checking

// Function to fetch API status
const fetchApiStatus = async () => {
  try {
    await axios.get("http://localhost:5000/"); // Adjust URL as needed
    apiStatus.value = 'online'; // API is online
  } catch (error) {
    console.error("Error fetching API status:", error);
    apiStatus.value = 'offline'; // API is offline
  }
};

// Function to fetch bot status
const fetchBotStatus = async () => {
  try {
    
    const response = await axios.get("http://localhost:5000/logs");
    logs.value = response.data || [];

    if (logs.value.length > 0) {
      lastLog.value = logs.value[0];
      const lastTimestamp = new Date(lastLog.value.timestamp);
      currentTime.value = new Date();
      timeDifference.value = Math.floor((currentTime.value - lastTimestamp) / 1000); // Time difference in seconds

      // Determine bot status
      if (timeDifference.value < 300) {
        if (lastLog.value.action === "GET /bot") {
          botStatus.value = 'online';
        } else if (lastLog.value.action === "POST /bot") {
          botStatus.value = 'online';
        }
      }
    }  
  } catch (error) {
    console.error("Error fetching bot status:", error);
    botStatus.value = 'offline'; // Bot is offline
  }
};

// Set interval to refresh data every minute (60000 ms)
let intervalId;

onMounted(() => {
  fetchApiStatus(); // Fetch initial data
  fetchBotStatus();

  // Set interval for periodic refresh
  intervalId = setInterval(() => {
    fetchApiStatus();
    fetchBotStatus();
  }, 30000); // 30 s 
});

onUnmounted(() => {
  clearInterval(intervalId); // Clear the interval when component is destroyed
});

</script>

<style scoped>
/* Custom styling for the badges */
.badge-status {
  font-size: 4.5rem; /* Three times the previous size (1.5rem -> 4.5rem) */
  margin-left: 15px; /* Space between badges */
  margin-right: 15px; /* Space from the right edge */
  
  /* Adding border */
  border-radius: 20px; /* Rounded corners */
  padding: 30px 40px; /* Add some padding for better appearance */
}

/* Ensuring the badges are centered */
.v-toolbar-title {
  flex-grow: 1;
}
</style>
