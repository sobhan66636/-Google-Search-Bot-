<template>
  <v-footer
    app
    color="primary"
    dark
    class="custom-footer"
  >
    <v-spacer />
    <v-col
      class="text-center"
      cols="12"
    >
      <p>&copy; 2025 S.M . All rights reserved.</p>
    </v-col>
  </v-footer>
</template>

<script setup>
</script>

<style scoped>
/* Make footer smaller */
.custom-footer {
  max-height: 25px;  /* Adjust this value to make the footer smaller */
}
</style>
