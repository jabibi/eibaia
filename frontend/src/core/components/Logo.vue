<script setup lang="ts">
withDefaults(defineProps<{ width?: number; height?: number }>(), { width: 260, height: 370 });
</script>

<template>
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="120 55 260 370" :width="width" :height="height" class="select-none">
    <!-- Ilustración Central -->
    <g transform="translate(250, 197) scale(1.5)">
      <!-- 1. SOL (Fondo lejano) -->
      <g transform="translate(0, -54)">
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

      <!-- 2. LAGO EN SEGUNDO PLANO -->
      <g transform="translate(0, -18)">
        <path d="M -78,14 C -45,4 0,18 45,8 C 65,4 78,12 78,22 C 78,30 45,30 0,32 C -45,34 -78,28 -78,14 Z" fill="#7dd3fc" opacity="0.9" />
        <path d="M -68,18 C -35,10 10,24 58,14 C 70,12 74,18 60,22 C 25,27 -30,29 -68,22 Z" fill="#38bdf8" />
        <path d="M -52,24 C -20,18 15,28 50,22 C 58,21 45,28 10,30 C -25,32 -48,29 -52,24 Z" fill="#0284c7" />
      </g>

      <!-- 3. PINOS EN PLANO MEDIO -->
      <polygon points="-60,26 -40,-22 -20,26" fill="#166534" />
      <polygon points="-60,6 -40,-32 -20,6" fill="#15803d" />
      <polygon points="-44,40 -26,-12 -8,40" fill="#14532d" />
      <polygon points="-44,20 -26,-22 -8,20" fill="#166534" />

      <polygon points="20,26 40,-22 60,26" fill="#166534" />
      <polygon points="20,6 40,-32 60,6" fill="#15803d" />
      <polygon points="8,40 26,-12 44,40" fill="#14532d" />
      <polygon points="8,20 26,-22 44,20" fill="#166534" />

      <!-- 4. CASERÍO EN PRIMER PLANO -->
      <rect x="-28" y="0" width="56" height="44" fill="#f5f5f4" />
      <rect x="-28" y="44" width="56" height="5" fill="#d6d3d1" />

      <polygon points="-37,0 0,-23 37,0" fill="#b91c1c" />
      <polygon points="-28,0 0,-16 28,0" fill="#dc2626" />

      <rect x="-14" y="6" width="28" height="8" rx="0.5" fill="#5c3a21" />
      <rect x="-14" y="6" width="28" height="2" fill="#3d2413" />

      <rect x="-23" y="19" width="8" height="10" fill="#4a3121" />
      <rect x="15" y="19" width="8" height="10" fill="#4a3121" />

      <rect x="5" y="28" width="18" height="18" fill="#1c120c" />
      <rect x="-21" y="30" width="10" height="12" fill="#1c120c" />

      <polygon points="-8,47 -3,22 1,1 6,27 3,47 -2,42" fill="#15803d" />
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
