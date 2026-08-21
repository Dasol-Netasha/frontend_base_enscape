<script setup>
import { computed } from 'vue'

const props = defineProps({
	type: {
		type: String,
		default: 'button'
	},
	variant: {
		type: String,
		default: 'primary'
	},
	size: {
		type: String,
		default: 'md'
	},
	disabled: {
		type: Boolean,
		default: false
	},
	block: {
		type: Boolean,
		default: false
	},
	rounded: {
		type: Boolean,
		default: false
	},
	outlined: {
		type: Boolean,
		default: false
	},
	flat: {
		type: Boolean,
		default: false
	}
})

const emit = defineEmits(['click'])

const variantClass = computed(() => {
	const variants = {
		primary: 'btn-primary',
		secondary: 'btn-secondary',
		danger: 'btn-danger',
		ghost: 'btn-ghost'
	}

	return variants[props.variant] ?? variants.primary
})

const sizeClass = computed(() => {
	const sizes = {
		sm: 'btn-sm',
		md: 'btn-md',
		lg: 'btn-lg'
	}

	return sizes[props.size] ?? sizes.md
})

const flatSizeClass = computed(() => {
	const sizes = {
		sm: 'btn-flat-sm',
		md: 'btn-flat-md',
		lg: 'btn-flat-lg'
	}

	return sizes[props.size] ?? sizes.md
})

const outlinedClass = computed(() => {
	const outlinedVariants = {
		primary: 'btn-outlined-primary',
		secondary: 'btn-outlined-secondary',
		danger: 'btn-outlined-danger',
		ghost: 'btn-outlined-ghost'
	}

	return outlinedVariants[props.variant] ?? outlinedVariants.primary
})

const blockClass = computed(() => (props.block ? 'w-full' : 'w-auto'))
const roundedClass = computed(() => (props.rounded ? 'btn-rounded' : ''))
const appearanceClass = computed(() => {
	if (props.outlined) {
		return ['btn-outlined', outlinedClass.value]
	}

	return [variantClass.value]
})

const interactionClass = computed(() => (props.flat ? ['btn-flat', flatSizeClass.value] : [sizeClass.value]))

const handleClick = (event) => {
	if (!props.disabled) {
		emit('click', event)
	}
}
</script>

<template>
	<button
		:type="type"
		:disabled="disabled"
		class="btn-base"
		:class="[appearanceClass, interactionClass, blockClass, roundedClass]"
		@click="handleClick"
	>
		<slot />
	</button>
</template>
