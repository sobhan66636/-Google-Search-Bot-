<template>
  <v-card>
    <!-- Bot Status Section -->
    <v-card-title>Bot Status</v-card-title>
    <v-card-text>
      <v-alert
        v-if="botStatusMessage"
        :type="botStatusMessage.includes('inactive') ? 'error' : 'success'"
        dense
        outlined
        class="mb-4"
        :style="{ borderColor: botStatusMessage.includes('inactive') ? 'red' : 'green', color: botStatusMessage.includes('inactive') ? 'red' : 'green' }"
      >
        {{ botStatusMessage }}
      </v-alert>
    </v-card-text>

    <!-- Logs Viewer Section -->
    <v-card-title>API Log Viewer</v-card-title>
    <v-card-text>
      <v-data-table
        v-if="logs.length > 0"
        :headers="tableHeaders"
        :items="logs"
        item-value="id"
        class="elevation-1"
        dense
        style="max-height: 400px; overflow-y: auto;"
      >
        <template #[`item.timestamp`]="{ item }">
          <span>{{ formatTimestamp(item.timestamp) }}</span>
        </template>

        <template #[`item.action`]="{ item }">
          <span>{{ item.action || 'N/A' }}</span>
        </template>

        <template #[`item.details`]="{ item }">
          <span>{{ item.details || 'N/A' }}</span>
        </template>

        <template #[`item.ip_address`]="{ item }">
          <span>{{ item.ip_address || 'N/A' }}</span>
        </template>

        <template #[`item.http_method`]="{ item }">
          <span>{{ item.http_method || 'N/A' }}</span>
        </template>

        <template #[`item.path`]="{ item }">
          <span>{{ item.path || 'N/A' }}</span>
        </template>

        <template #[`item.status_code`]="{ item }">
          <span>{{ item.status_code || 'N/A' }}</span>
        </template>
      </v-data-table>

      <v-alert
        v-if="logs.length === 0"
        type="info"
        outlined
        class="mt-4"
      >
        No logs available to display.
      </v-alert>

      <v-alert
        v-if="errorMessage"
        type="error"
        outlined
        class="mt-4"
      >
        {{ errorMessage }}
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, onMounted,onUnmounted } from "vue";
import axios from "axios";

// State variables for logs, error handling, and bot status
const logs = ref([]);
const errorMessage = ref(null);
const botStatusMessage = ref("Fetching bot status...");
const lastLog = ref(null);
const timeDifference = ref(null);
const currentTime = ref(new Date());

// Table headers for logs
const tableHeaders = [
  { title: "Timestamp", align: "start", key: "timestamp" },
  { title: "Action", align: "start", key: "action" },
  { title: "Details", align: "start", key: "details" },
  { title: "IP Address", align: "start", key: "ip_address" },
  { title: "HTTP Method", align: "start", key: "http_method" },
  { title: "Path", align: "start", key: "path" },
  { title: "Status Code", align: "start", key: "status_code" }
];

// Function to fetch logs from the backend
const fetchLogs = async () => {
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
          botStatusMessage.value = "Bot is searching ...";
        } else if (lastLog.value.action === "POST /bot") {
          botStatusMessage.value = "Bot is sending results ...";
        } 
      } else {
        botStatusMessage.value = "Bot is inactive (last activity over 5 minutes ago).";
      }
    } else {
      botStatusMessage.value = "No logs found. Bot might be inactive.";
    }
  } catch (error) {
    console.error("Error fetching logs:", error);
    errorMessage.value = "Failed to fetch logs. Please try again later.";
    botStatusMessage.value = "Error fetching bot status.";
  }
};

// Format timestamp to a readable format
const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleString();
};

// Set interval to refresh data every minute (60000 ms)
let intervalId;

onMounted(() => {
  fetchLogs(); // Fetch initial data

  // Set interval for periodic refresh
  intervalId = setInterval(() => {
    fetchLogs();
  }, 30000); // 1 minute
});

onUnmounted(() => {
  clearInterval(intervalId); // Clear the interval when component is destroyed
});
</script>

<style scoped>
.v-data-table {
  overflow-y: auto;
}
.mb-4 {
  margin-bottom: 1rem;
}
</style>
