<script setup>
import ThemeToggleIconBtn from '@/components/molecules/buttons/ThemeToggleIconBtn.vue'
import { useThemeStore } from '@/stores/themeStore'

const themeStore = useThemeStore()
</script>

<template>
	<div class="flex items-center justify-between gap-3">
		<span class="text-sm font-semibold text-slate-700">Base</span>
		<ThemeToggleIconBtn
			:is-dark="themeStore.isDark"
			@click="themeStore.toggleTheme"
		/>
	</div>
</template>