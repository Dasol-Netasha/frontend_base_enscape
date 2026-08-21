<script setup>
import ButtonNav from '@/components/organisms/nav/ButtonNav.vue'

defineProps({
	items: {
		type: Array,
		default: () => [],
	},
})
</script>

<template>
	<ButtonNav v-if="items.length" :items="items" align="center" />
</template>