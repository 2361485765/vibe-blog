/**
 * 101.05 引用悬浮卡片 — CitationTooltip 组件测试
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CitationTooltip from '@/components/generate/CitationTooltip.vue'

const mockCitation = {
  url: 'https://langchain-ai.github.io/langgraph/',
  title: 'LangGraph: Multi-Agent Workflows',
  domain: 'langchain-ai.github.io',
  snippet: 'A framework for building stateful, multi-actor applications with LLMs.',
  relevance: 95,
}

describe('CitationTooltip.vue', () => {
  it('should render when visible with citation data', () => {
    const wrapper = mount(CitationTooltip, {
      props: { visible: true, citation: mockCitation, index: 1, position: { top: 100, left: 200 } },
    })
    expect(wrapper.find('.citation-tooltip').exists()).toBe(true)
  })

  it('should not render when not visible', () => {
    const wrapper = mount(CitationTooltip, {
      props: { visible: false, citation: mockCitation, index: 1, position: { top: 0, left: 0 } },
    })
    expect(wrapper.find('.citation-tooltip').exists()).toBe(false)
  })

  it('should not render when citation is null', () => {
    const wrapper = mount(CitationTooltip, {
      props: { visible: true, citation: null, index: 1, position: { top: 0, left: 0 } },
    })
    expect(wrapper.find('.citation-tooltip').exists()).toBe(false)
  })

  it('should render citation index', () => {
    const wrapper = mount(CitationTooltip, {
      props: { visible: true, citation: mockCitation, index: 3, position: { top: 0, left: 0 } },
    })
    expect(wrapper.find('.citation-index').text()).toContain('[3]')
  })

  it('should render domain', () => {
    const wrapper = mount(CitationTooltip, {
      props: { visible: true, citation: mockCitation, index: 1, position: { top: 0, left: 0 } },
    })
    expect(wrapper.find('.citation-domain').text()).toContain('langchain-ai.github.io')
  })

  it('should render title', () => {
    const wrapper = mount(CitationTooltip, {
      props: { visible: true, citation: mockCitation, index: 1, position: { top: 0, left: 0 } },
    })
    expect(wrapper.find('.citation-title').text()).toContain('LangGraph')
  })

  it('should render snippet', () => {
    const wrapper = mount(CitationTooltip, {
      props: { visible: true, citation: mockCitation, index: 1, position: { top: 0, left: 0 } },
    })
    expect(wrapper.find('.citation-snippet').text()).toContain('multi-actor')
  })

  it('should render relevance when available', () => {
    const wrapper = mount(CitationTooltip, {
      props: { visible: true, citation: mockCitation, index: 1, position: { top: 0, left: 0 } },
    })
    expect(wrapper.find('.citation-relevance').text()).toContain('95%')
  })

  it('should not render relevance when not available', () => {
    const noRelevance = { ...mockCitation, relevance: undefined }
    const wrapper = mount(CitationTooltip, {
      props: { visible: true, citation: noRelevance, index: 1, position: { top: 0, left: 0 } },
    })
    expect(wrapper.find('.citation-relevance').exists()).toBe(false)
  })

  it('should render open link with correct href', () => {
    const wrapper = mount(CitationTooltip, {
      props: { visible: true, citation: mockCitation, index: 1, position: { top: 0, left: 0 } },
    })
    const link = wrapper.find('.citation-link')
    expect(link.attributes('href')).toBe('https://langchain-ai.github.io/langgraph/')
    expect(link.attributes('target')).toBe('_blank')
  })

  it('should position at given coordinates', () => {
    const wrapper = mount(CitationTooltip, {
      props: { visible: true, citation: mockCitation, index: 1, position: { top: 150, left: 300 } },
    })
    const style = wrapper.find('.citation-tooltip').attributes('style')
    expect(style).toContain('top: 150px')
    expect(style).toContain('left: 300px')
  })
})
