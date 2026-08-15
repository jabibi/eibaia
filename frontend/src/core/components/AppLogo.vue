<script setup lang="ts">
withDefaults(defineProps<{ width?: number; height?: number }>(), { width: 260, height: 370 });
</script>

<template>
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="120 55 260 370" :width="width" :height="height">
    <!-- Central circular emblem -->
    <g transform="translate(250, 175)">
      <!-- Outer dashed circle -->
      <circle cx="0" cy="0" r="105" fill="none" stroke="#15803d" stroke-width="2.5" stroke-dasharray="7 5" />

      <!-- Inner light mint circle -->
      <circle cx="0" cy="0" r="92" fill="#edf9f1" stroke="#bbf7d0" stroke-width="1.5" />

      <g>
        <!-- Sun -->
        <g transform="translate(0, -48)">
          <circle cx="0" cy="0" r="11" fill="#f59e0b" />
          <circle cx="0" cy="0" r="5.5" fill="#fef3c7" />
          <circle cx="0" cy="0" r="2.5" fill="#d97706" />
          <g stroke="#f59e0b" stroke-width="2.2" stroke-linecap="round">
            <line x1="0" y1="-16" x2="0" y2="-20" />
            <line x1="0" y1="16" x2="0" y2="20" />
            <line x1="-16" y1="0" x2="-20" y2="0" />
            <line x1="16" y1="0" x2="20" y2="0" />
            <line x1="-11" y1="-11" x2="-14" y2="-14" />
            <line x1="11" y1="-11" x2="14" y2="-14" />
            <line x1="-11" y1="11" x2="-14" y2="14" />
            <line x1="11" y1="11" x2="14" y2="14" />
          </g>
        </g>

        <!-- Left pine trees -->
        <polygon points="-54,30 -34,-18 -14,30" fill="#166534" />
        <polygon points="-54,10 -34,-28 -14,10" fill="#15803d" />
        <polygon points="-38,44 -20,-8 -2,44" fill="#14532d" />
        <polygon points="-38,24 -20,-18 -2,24" fill="#166534" />

        <!-- Right pine trees -->
        <polygon points="14,30 34,-18 54,30" fill="#166534" />
        <polygon points="14,10 34,-28 54,10" fill="#15803d" />
        <polygon points="2,44 20,-8 38,44" fill="#14532d" />
        <polygon points="2,24 20,-18 38,24" fill="#166534" />

        <!-- Farmhouse / red house -->
        <rect x="-19" y="6" width="38" height="40" fill="#dc2626" />
        <polygon points="-27,6 0,-20 27,6" fill="#b91c1c" />
        <path d="M-7,46 L-7,25 A 7,7 0 0,1 7,25 L7,46 Z" fill="#ffffff" />
        <circle cx="0" cy="-5" r="3" fill="#fef3c7" />
      </g>
    </g>

    <!-- Logo wordmark -->
    <text
      x="250"
      y="340"
      text-anchor="middle"
      font-family="'Inter', 'Segoe UI', Arial, sans-serif"
      font-weight="800"
      font-size="44"
      fill="#15803d"
    >Elosu<tspan fill="#dc2626">E!</tspan></text>
    <text
      x="250"
      y="380"
      text-anchor="middle"
      font-family="'Inter', 'Segoe UI', Arial, sans-serif"
      font-weight="700"
      font-size="13.5"
      fill="#dc2626"
      letter-spacing="4.5"
    >GESTIÓN DEL HOGAR</text>
    <text
      x="250"
      y="408"
      text-anchor="middle"
      font-family="'Inter', 'Segoe UI', Arial, sans-serif"
      font-weight="600"
      font-size="11"
      fill="#64748b"
      letter-spacing="2"
    >HARITZ ONDO BASERRIA</text>
  </svg>
</template>
