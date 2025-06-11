<template> 
  <v-card>
    <v-card-title>Upload Keywords via Excel</v-card-title>
    <v-card-text>
      <v-form @submit.prevent="uploadExcel">
        <v-file-input
          label="Select Excel File"
          accept=".xlsx"
          dense
          outlined
          @change="onFileChange"
        />
        <v-btn
          type="submit"
          color="primary"
          class="mt-4"
          :disabled="!excelFile"
        >
          Upload
        </v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";

const excelFile = ref(null);

const onFileChange = (file) => {
  excelFile.value = file;
};

const uploadExcel = async () => {
  if (!excelFile.value) {
    alert("Please select an Excel file.");
    return;
  }

  const formData = new FormData();
  formData.append("file", excelFile.value);

  try {
    await axios.post("http://localhost:5000/upload_excel", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    alert("Excel file uploaded successfully.");
  } catch (error) {
    console.error("Error uploading Excel file:", error);
    alert("Failed to upload the Excel file.");
  }
};
</script>

<style scoped>
/* Add custom spacing or styles if necessary */
</style>