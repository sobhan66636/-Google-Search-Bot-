<template>
  <v-row class="section-row">
    <!-- Dashboard with Charts -->
    <v-row class="section-row">
      <v-col cols="12">
        <v-card>
          <v-card-title>Trend Chart</v-card-title>
          <v-card-text>
            <!-- Filters for Website and Keyword -->
            <v-row>
              <v-col
                cols="12"
                md="6"
              >
                <v-card-title>select:</v-card-title>
              </v-col>
            </v-row>

            <!-- Trend Chart Canvas -->
            <canvas
              ref="chartRef"
              class="chart-canvas"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-col cols="12">
      <v-card>
        <v-card-title>Number of Reviews</v-card-title>
        <v-card-text>
          <canvas
            ref="commentsChartRef"
            class="chart-canvas"
          />
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>

  <v-data-table
    :headers="filterHeaders"
    :items="filteredKeywordData"
    item-key="id"
    :items-per-page="itemsPerPage"
    :footer-props="{
      'items-per-page-options': [10, 25, 50],
      'show-current-page': true,
      'show-items-per-page': true
    }"
  >
    <!-- Template for the Date column -->
    <template #[`item.date`]="{ item }">
      <td>{{ [...new Set(item.dates.map(date => new Date(date).getDate()))].join(', ') }}</td>
    </template>

    <template #top>
      <v-row>
        <v-col
          cols="12"
          md="4"
        >
          <v-select
            v-model="selectedSiteFilter"
            :items="siteOptions"
            label="Select Site"
            clearable
            multiple
          />
        </v-col>
        <v-col
          cols="12"
          md="4"
        >
          <v-select
            v-model="selectedKeywordFilter"
            :items="keywordOptions"
            label="Select Keyword"
            clearable
            multiple
          />
        </v-col>
        <v-col
          cols="12"
          md="4"
        >
          <v-select
            v-model="selectedDayFilter"
            :items="dayOptions"
            label="Select Day"
            clearable
            multiple
          />
        </v-col>
      </v-row>
    </template>
  </v-data-table>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount ,onUnmounted} from 'vue';
import axios from 'axios'; // Make sure to install axios
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

const chartRef = ref(null);
const commentsChartRef = ref(null);

const selectedSiteFilter = ref([]);
const selectedKeywordFilter = ref([]);
const selectedDayFilter = ref([]);

const siteOptions = ref([]);
const keywordOptions = ref([]);
const dayOptions = ref([]);

const keywordData = ref([]);

const filterHeaders = [
  { title: 'Keyword', key: 'keyword' },
  { title: 'Related Site', key: 'site' },
  { title: 'Lowest Rank', key: 'lowestRank' },
  { title: 'Highest Rank', key: 'highestRank' },
  { title: 'Average Rank', key: 'averageRank' },
  { title: 'Number of Reviews', key: 'numReviews' },
  { title: 'Date', key: 'date' }   
];

const filteredKeywordData = computed(() => {
  return keywordData.value
    .filter(item => {
      // Filter by site
      const matchesSite = selectedSiteFilter.value.length === 0 || selectedSiteFilter.value.includes(item.site);
      
      // Filter by keyword
      const matchesKeyword = selectedKeywordFilter.value.length === 0 || selectedKeywordFilter.value.includes(item.keyword);
      
      // If no day is selected, show all data
      const matchesDay = selectedDayFilter.value.length === 0 || item.dates.some(date => selectedDayFilter.value.includes(date));

      // Only include the item if it matches site, keyword, and day (or all days if no day is selected)
      return matchesSite && matchesKeyword && matchesDay;
    })
    .map(item => {
      // If no day is selected, show all dates, ranks, and reviews
      if (selectedDayFilter.value.length === 0) {
        return item; // Return the full item with all dates, ranks, and reviews
      }
      
      // Otherwise, filter by the selected days
      const filteredDates = item.dates.filter(date => selectedDayFilter.value.includes(date));
      
      // Filter ranks (min, max, avg) for each corresponding date
      const filteredRanks = item.ranks.filter((rank, index) => selectedDayFilter.value.includes(item.dates[index]));

      // Filter min, max, and avg ranks for the selected days
      const filteredMinRank = Math.min(...filteredRanks);
      const filteredMaxRank = Math.max(...filteredRanks);
      const filteredAvgRank = filteredRanks.length > 0 ? filteredRanks.reduce((sum, rank) => sum + rank, 0) / filteredRanks.length : 0;

      // Return the item with filtered dates, ranks, and recalculated min, max, and avg ranks
      return {
        ...item,
        dates: filteredDates,
        lowestRank: filteredMinRank,
        highestRank: filteredMaxRank,
        averageRank: filteredAvgRank, 
        numReviews: filteredRanks.length, // Set the number of reviews to match the filtered ranks
      };
    });
});


const createCommentsChart = (keywords, reviews) => {
  const ctx = commentsChartRef.value.getContext("2d");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: keywords, // Dynamically set labels (fetched keywords)
      datasets: [
        {
          label: "Number of Reviews",
          data: reviews, // Dynamically set data (number of reviews)
          backgroundColor: "rgba(153, 102, 255, 0.2)",
          borderColor: "rgba(153, 102, 255, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true },
      },
    },
  });
};
// Fetch data from API
const fetchKeywordData = async () => {
  try {
    const response = await axios.get('http://localhost:5000/results');
    const results = response.data.results;

    // Log the response to check the structure
    console.log('API Response:', results);

    // Create an array to store data (keyword-site combination)
    const combinedData = [];

    // Group the data by keyword and site
    results.forEach(item => {
      const existing = combinedData.find(
        data => data.keyword === item.keyword && data.site === item.website.name
      );

      if (existing) {
        // Update existing entry if same keyword and site
        existing.numReviews += 1;
        existing.lowestRank = Math.min(existing.lowestRank, item.min_rank);
        existing.highestRank = Math.max(existing.highestRank, item.max_rank);
        existing.totalRank += item.avg_rank;
        existing.dates.push(new Date(item.timestamp).toLocaleDateString());
        existing.ranks.push(item.avg_rank);
      } else {
        // Add a new entry for new keyword-site combination
        combinedData.push({
          id: `${item.keyword}-${item.website.name}`,
          keyword: item.keyword,
          site: item.website.name,
          lowestRank: item.min_rank,
          highestRank: item.max_rank,
          averageRank: item.avg_rank,
          numReviews: 1,
          totalRank: item.avg_rank,
          dates: [new Date(item.timestamp).toLocaleDateString()],
          ranks: [item.avg_rank],
        });
      }
    });

    // Now set the processed data to keywordData
    keywordData.value = combinedData;

    // Fill siteOptions, keywordOptions, and dayOptions from the fetched data
    siteOptions.value = [...new Set(results.map(item => item.website.name))];
    keywordOptions.value = [...new Set(results.map(item => item.keyword))];
    dayOptions.value = [...new Set(results.map(item => new Date(item.timestamp).toLocaleDateString()))];
    

    // Pass data to createChart (Trend chart)
    createChart(combinedData);

    // Aggregate reviews for the same keyword (combine entries with the same keyword)
    const aggregatedKeywordData = combinedData.reduce((acc, item) => {
      const existing = acc.find(data => data.keyword === item.keyword);
      if (existing) {
        existing.numReviews += item.numReviews; // Combine the number of reviews
        existing.totalRank += item.totalRank; // Combine the rank totals
      } else {
        acc.push({
          keyword: item.keyword,
          numReviews: item.numReviews,
          totalRank: item.totalRank,
        });
      }
      return acc;
    }, []);

    // Extract keywords and reviews for the "Number of Reviews" chart
    const keywords = aggregatedKeywordData.map(group => group.keyword);
    const reviews = aggregatedKeywordData.map(group => group.numReviews);

    // Pass data to createCommentsChart (Number of Reviews chart)
    createCommentsChart(keywords, reviews);

  } catch (error) {
    console.error('Error fetching data:', error);
  }
};
const createChart = (combinedData) => {
  const ctx = chartRef.value.getContext("2d");

  // Get selected filters
  const selectedKeywords = selectedKeywordFilter.value;
  const selectedSites = selectedSiteFilter.value;

  // Filter the combinedData based on the selected filters
  const filteredData = combinedData.filter(item => {
    const matchesKeyword = selectedKeywords.length === 0 || selectedKeywords.includes(item.keyword);
    const matchesSite = selectedSites.length === 0 || selectedSites.includes(item.site);
    const matchesDay = selectedDayFilter.value.length === 0 || selectedDayFilter.value.includes(item.dates);
    return matchesSite && matchesKeyword && matchesDay;
  });

  // Create a random color for each keyword-site combination
  const getRandomColor = () => {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  };

  // Prepare the data for the chart
  const datasets = filteredData.map(item => ({
    label: `${item.keyword} - ${item.site}`,
    data: item.ranks,  // Ranks over time for this combination
    borderColor: getRandomColor(),
    backgroundColor: 'transparent',
    borderWidth: 2,
    fill: false,
    pointBackgroundColor: 'transparent'
  }));

  // Create the chart with the filtered data
  new Chart(ctx, {
    type: "line",
    data: {
      labels: filteredData.length > 0 ? filteredData[0].dates : [], // Use the date from any of the datasets
      datasets: datasets,
    },
    options: {
      responsive: true,
      scales: {
        x: { title: { display: true, text: "Date" } , },
        y: { title: { display: true, text: "Rank" }, reverse: true },
      },
    },
  });
};
let intervalId;

onMounted(() => {
  fetchKeywordData();

  intervalId = setInterval(() => {
    fetchKeywordData();
  }, 120000); // 2 minute
});
onUnmounted(() => {
  clearInterval(intervalId); // Clear the interval when component is destroyed
  
});
onBeforeUnmount(() => {
  if (chartRef.value) {
    chartRef.value.destroy();
  }
  if (commentsChartRef.value) {
    commentsChartRef.value.destroy();
  }
});
</script>

<style scoped>
/* Global Styles */
.v-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-row {
  margin-bottom: 20px;
}

.v-card {
  margin-bottom: 20px;
}

.v-navigation-drawer {
  width: 250px;
}

.v-text-field {
  max-width: 300px;
}

.chart-canvas {
  width: 100% !important;
  height: 400px !important;
}

@media (max-width: 600px) {
  .chart-canvas {
    height: 250px !important;
  }
}
</style>
