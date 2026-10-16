/**
 * v-reveal：元素进入视口时加上 .is-visible，触发 motion.css 中的 .reveal 动画。
 *   <li v-for="(x, i) in list" v-reveal="i">   // 传入序号即可错峰出现
 * 所有元素共用一个 IntersectionObserver；不支持 IO 的环境直接显示。
 */
type Binding = { value?: number }

let io: IntersectionObserver | null = null

function observer(): IntersectionObserver | null {
  if (io || typeof IntersectionObserver === 'undefined') return io
  io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue
        e.target.classList.add('is-visible')
        io!.unobserve(e.target)
      }
    },
    { rootMargin: '0px 0px -8% 0px', threshold: 0.01 },
  )
  return io
}

export const vReveal = {
  mounted(el: HTMLElement, binding: Binding) {
    el.classList.add('reveal')
    // 错峰上限，避免长列表尾部等待太久
    el.style.setProperty('--i', String(Math.min(binding.value ?? 0, 12)))
    const o = observer()
    if (o) o.observe(el)
    else el.classList.add('is-visible')
  },
  unmounted(el: HTMLElement) {
    io?.unobserve(el)
  },
}

/** <img @load="onImgLoad"> 配合 .img-fade 使用 */
export function onImgLoad(e: Event) {
  ;(e.target as HTMLElement).classList.add('is-loaded')
}
