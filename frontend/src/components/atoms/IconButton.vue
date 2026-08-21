<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'button'
  },
  variant: {
    type: String,
    default: 'ghost'
  },
  size: {
    type: String,
    default: 'md'
  },
  disabled: {
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
  },
  ariaLabel: {
    type: String,
    default: 'icon button'
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

  return variants[props.variant] ?? variants.ghost
})

const iconSizeClass = computed(() => {
  const sizes = {
    sm: 'icon-svg-sm',
    md: 'icon-svg-md',
    lg: 'icon-svg-lg'
  }

  return sizes[props.size] ?? sizes.md
})

const buttonSizeClass = computed(() => {
  const sizes = {
    sm: 'btn-icon-sm',
    md: 'btn-icon-md',
    lg: 'btn-icon-lg'
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

  return outlinedVariants[props.variant] ?? outlinedVariants.ghost
})

const appearanceClass = computed(() => {
  if (props.outlined) {
    return ['btn-outlined', outlinedClass.value]
  }

  return [variantClass.value]
})

const interactionClass = computed(() => (props.flat ? ['btn-flat', 'btn-icon-flat'] : [buttonSizeClass.value]))

const roundedClass = computed(() => (props.rounded ? 'btn-rounded' : ''))

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
    class="btn-base btn-icon"
    :class="[appearanceClass, interactionClass, iconSizeClass, roundedClass]"
    :aria-label="ariaLabel"
    @click="handleClick"
  >
    <span class="icon-svg">
      <slot />
    </span>
  </button>
</template>
