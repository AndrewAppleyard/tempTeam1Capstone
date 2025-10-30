<script setup>
    import { ref } from 'vue';

    const inputRef = ref();

    function focusInput() {
        inputRef.value.focus();
    }

    defineExpose({
        focusInput
    });
</script>

<template>
    <v-text-field
      ref="inputRef"
      label="Focusable Input"
    ></v-text-field>
</template>