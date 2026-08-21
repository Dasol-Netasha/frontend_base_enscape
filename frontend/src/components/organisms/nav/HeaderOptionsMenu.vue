<script setup>
import { computed } from 'vue'
import Dropdown from '@/components/organisms/dropdown/Dropdown.vue'
import DropdownMenu from '@/components/molecules/dropdown/DropdownMenu.vue'
import IconButton from '@/components/atoms/IconButton.vue'
import SettingsIcon from '@/components/atoms/icons/SettingsIcon.vue'
import SunIcon from '@/components/atoms/icons/SunIcon.vue'
import MoonIcon from '@/components/atoms/icons/MoonIcon.vue'
import { useThemeStore } from '@/stores/themeStore'

const emit = defineEmits(['logout', 'options'])

const themeStore = useThemeStore()

const items = computed(() => [
  {
    key: 'theme',
    label: themeStore.isDark ? '라이트 모드로 변경' : '다크 모드로 변경',
    icon: themeStore.isDark ? SunIcon : MoonIcon,
  },
  { key: 'options', label: '옵션', icon: SettingsIcon },
  { type: 'divider' },
  { key: 'logout', label: '로그아웃', danger: true },
])

const handleSelect = (item, close) => {
  if (item.key === 'theme') {
    themeStore.toggleTheme()
  } else if (item.key === 'options') {
    emit('options')
  } else if (item.key === 'logout') {
    emit('logout')
  }
  close()
}
</script>

<template>
  <Dropdown align="end">
    <template #trigger="{ toggle, isOpen, panelId }">
      <IconButton
        variant="ghost"
        rounded
        outlined
        aria-label="옵션 메뉴"
        :aria-expanded="isOpen"
        :aria-controls="panelId"
        @click="toggle"
      >
        <SettingsIcon />
      </IconButton>
    </template>

    <template #default="{ close }">
      <DropdownMenu :items="items" @select="(item) => handleSelect(item, close)" />
    </template>
  </Dropdown>
</template>
