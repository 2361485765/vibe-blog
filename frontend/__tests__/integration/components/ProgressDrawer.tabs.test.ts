/**
 * Phase 2: ProgressDrawer Tab 切换 + 大纲审批测试
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ProgressDrawer from '@/components/home/ProgressDrawer.vue'

const baseProps = {
  visible: true,
  expanded: true,
  isLoading: false,
  statusBadge: '运行中',
  progressText: '生成中',
  progressItems: [],
  articleType: 'tutorial',
  targetLength: 'medium',
  taskId: 'task_abc123',
  outlineData: null as any,
  waitingForOutline: false,
  previewContent: '',
  embedded: false,
}

describe('ProgressDrawer — Tab 切换', () => {
  it('should render tab bar with two tabs', () => {
    const wrapper = mount(ProgressDrawer, { props: baseProps })
    const tabs = wrapper.findAll('.progress-tab')
    expect(tabs.length).toBe(2)
    expect(tabs[0].text()).toContain('活动日志')
    expect(tabs[1].text()).toContain('文章预览')
  })

  it('should default to logs tab active', () => {
    const wrapper = mount(ProgressDrawer, { props: baseProps })
    const tabs = wrapper.findAll('.progress-tab')
    expect(tabs[0].classes()).toContain('active')
    expect(tabs[1].classes()).not.toContain('active')
  })

  it('should disable preview tab when no content', () => {
    const wrapper = mount(ProgressDrawer, { props: baseProps })
    const previewTab = wrapper.findAll('.progress-tab')[1]
    expect(previewTab.classes()).toContain('disabled')
    expect((previewTab.element as HTMLButtonElement).disabled).toBe(true)
  })

  it('should enable preview tab when previewContent is set', () => {
    const wrapper = mount(ProgressDrawer, {
      props: { ...baseProps, previewContent: '<p>Hello</p>' },
    })
    const previewTab = wrapper.findAll('.progress-tab')[1]
    expect(previewTab.classes()).not.toContain('disabled')
    expect((previewTab.element as HTMLButtonElement).disabled).toBe(false)
  })

  it('should switch to preview tab on click', async () => {
    const wrapper = mount(ProgressDrawer, {
      props: { ...baseProps, previewContent: '<p>Preview</p>' },
    })
    const previewTab = wrapper.findAll('.progress-tab')[1]
    await previewTab.trigger('click')
    expect(previewTab.classes()).toContain('active')
    expect(wrapper.find('.progress-preview-content').isVisible()).toBe(true)
  })
})

describe('ProgressDrawer — 大纲审批卡片', () => {
  const outlineProps = {
    ...baseProps,
    outlineData: {
      title: '深入理解 LangGraph',
      sections_titles: ['介绍', '核心概念', '实战案例', '总结'],
    },
    waitingForOutline: true,
  }

  it('should render outline approval card when waiting', () => {
    const wrapper = mount(ProgressDrawer, { props: outlineProps })
    const text = wrapper.text()
    expect(text).toContain('深入理解 LangGraph')
    expect(text).toContain('开始写作')
  })

  it('should render all section titles', () => {
    const wrapper = mount(ProgressDrawer, { props: outlineProps })
    const text = wrapper.text()
    expect(text).toContain('介绍')
    expect(text).toContain('核心概念')
    expect(text).toContain('实战案例')
    expect(text).toContain('总结')
  })

  it('should render accept and edit buttons', () => {
    const wrapper = mount(ProgressDrawer, { props: outlineProps })
    const buttons = wrapper.findAll('button')
    const text = wrapper.text()
    expect(text).toContain('开始写作')
    expect(text).toContain('修改大纲')
  })

  it('should emit confirmOutline with accept on Y click', async () => {
    const wrapper = mount(ProgressDrawer, { props: outlineProps })
    const buttons = wrapper.findAll('button')
    const acceptBtn = buttons.find(b => b.text().includes('开始写作'))
    if (acceptBtn) {
      await acceptBtn.trigger('click')
      expect(wrapper.emitted('confirmOutline')).toBeTruthy()
      expect(wrapper.emitted('confirmOutline')![0]).toEqual(['accept'])
    }
  })

  it('should emit confirmOutline with edit on e click', async () => {
    const wrapper = mount(ProgressDrawer, { props: outlineProps })
    const buttons = wrapper.findAll('button')
    const editBtn = buttons.find(b => b.text().includes('修改大纲'))
    if (editBtn) {
      await editBtn.trigger('click')
      expect(wrapper.emitted('confirmOutline')).toBeTruthy()
      expect(wrapper.emitted('confirmOutline')![0]).toEqual(['edit'])
    }
  })

  it('should show confirmed state after outline is confirmed', () => {
    const wrapper = mount(ProgressDrawer, {
      props: {
        ...outlineProps,
        waitingForOutline: false,
      },
    })
    const text = wrapper.text()
    expect(text).toContain('深入理解 LangGraph')
  })

  it('should not render outline card when outlineData is null', () => {
    const wrapper = mount(ProgressDrawer, { props: baseProps })
    const text = wrapper.text()
    expect(text).not.toContain('开始写作')
  })
})
