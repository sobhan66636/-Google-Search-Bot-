<script setup lang="ts">

</script>

<template>
  <v-container>
    <Header />
    <v-main>
      <v-container>
        <!-- Website and Keyword Managers -->
        <v-row id="website-manager">
          <v-col
            cols="12"
            md="6"
          >
            <WebsiteManager />
          </v-col>
          <v-col
            cols="12"
            md="6"
          >
            <KeywordManager />
          </v-col>
        </v-row>

        <!-- Excel Uploader -->
        <v-row id="excel-uploader">
          <v-col cols="12">
            <ExcelUploader />
          </v-col>
        </v-row>

        <!-- Dashboard -->
        <v-row id="dashboard">
          <v-col cols="12">
            <Dashboard />
          </v-col>
        </v-row>
        <!-- Bot Status -->
        <v-row id="bot-status">
          <v-col cols="12">
            <BotStatus />
          </v-col>
        </v-row>
        
        <!-- Log Viewer -->
        <v-row id="log-viewer">
          <v-col cols="12">
            <LogViewer />
          </v-col>
        </v-row>
        <!-- suggestions Viewer -->
        <v-row id="log-viewer">
          <v-col cols="12">
            <suggestions />
          </v-col>
        </v-row>
      </v-container>
    </v-main>
    <Footer />
  </v-container>
</template>
