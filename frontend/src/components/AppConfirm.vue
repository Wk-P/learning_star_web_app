<template>
  <Teleport to="body">
    <div v-if="confirmState.visible" class="modal-backdrop" @click.self="close(false)">
      <div class="modal">
        <div class="modal-header">
          <span>{{ confirmState.title }}</span>
          <button class="modal-close btn-ghost" @click="close(false)">✕</button>
        </div>
        <div class="modal-body" style="padding-top:16px">
          <p style="color:var(--c-text-2);line-height:1.7">{{ confirmState.message }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="close(false)">
            {{ confirmState.cancelText ?? '取消' }}
          </button>
          <button
            :class="['btn', confirmState.type === 'danger' ? 'btn-danger' : 'btn-primary']"
            @click="close(true)"
          >
            {{ confirmState.confirmText ?? '确认' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { confirmState, useConfirm } from '@/composables/useConfirm'
const { close } = useConfirm()
</script>
