<script setup>
import { computed } from 'vue'

const props = defineProps({
	modelValue: {
		type: [String, Number],
		default: ''
	},
	type: {
		type: String,
		default: 'text'
	},
	placeholder: {
		type: String,
		default: ''
	},
	size: {
		type: String,
		default: 'md'
	},
	disabled: {
		type: Boolean,
		default: false
	},
	readonly: {
		type: Boolean,
		default: false
	},
	invalid: {
		type: Boolean,
		default: false
	},
	rounded: {
		type: Boolean,
		default: false
	}
})

const emit = defineEmits(['update:modelValue', 'focus', 'blur', 'enter'])

const sizeClass = computed(() => {
	const sizes = {
		sm: 'input-sm',
		md: 'input-md',
		lg: 'input-lg'
	}

	return sizes[props.size] ?? sizes.md
})

const invalidClass = computed(() => (props.invalid ? 'input-invalid' : ''))
const roundedClass = computed(() => (props.rounded ? 'input-rounded' : ''))

const handleInput = (event) => {
	emit('update:modelValue', event.target.value)
}

const handleKeydown = (event) => {
	if (event.key === 'Enter') {
		emit('enter', event)
	}
}
</script>

<template>
	<input
		:value="modelValue"
		:type="type"
		:placeholder="placeholder"
		:disabled="disabled"
		:readonly="readonly"
		class="input-base"
		:class="[sizeClass, invalidClass, roundedClass]"
		@input="handleInput"
		@focus="emit('focus', $event)"
		@blur="emit('blur', $event)"
		@keydown="handleKeydown"
	/>
</template>
