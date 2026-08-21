<script setup>
import { computed } from 'vue'

const props = defineProps({
	modelValue: {
		type: [String, Number],
		default: ''
	},
	options: {
		type: Array,
		default: () => []
	},
	size: {
		type: String,
		default: 'md'
	},
	disabled: {
		type: Boolean,
		default: false
	},
	invalid: {
		type: Boolean,
		default: false
	},
	placeholder: {
		type: String,
		default: '선택'
	}
})

const emit = defineEmits(['update:modelValue', 'change', 'focus', 'blur'])

const sizeClass = computed(() => {
	const sizes = {
		sm: 'px-2 py-1.5 text-sm',
		md: 'px-3 py-2 text-base',
		lg: 'px-4 py-3 text-lg'
	}
	return sizes[props.size] ?? sizes.md
})

const invalidClass = computed(() => (props.invalid ? 'border-rose-300 bg-rose-50' : ''))

const handleChange = (event) => {
	emit('update:modelValue', event.target.value)
	emit('change', event.target.value)
}
</script>

<template>
	<select
		:value="modelValue"
		:disabled="disabled"
		:class="`input-base ${sizeClass} text-slate-700 ${invalidClass}`"
		@change="handleChange"
		@focus="emit('focus', $event)"
		@blur="emit('blur', $event)"
	>
		<option v-if="placeholder" value="">{{ placeholder }}</option>
		<option v-for="opt in options" :key="opt.value" :value="opt.value">
			{{ opt.label }}
		</option>
	</select>
</template>
