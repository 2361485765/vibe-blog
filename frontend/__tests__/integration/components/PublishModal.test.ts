import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import PublishModal from '@/components/home/PublishModal.vue'

describe('PublishModal.vue', () => {
  const defaultProps = {
    visible: true,
    platform: 'csdn',
    cookie: '',
    isPublishing: false,
    status: '',
    statusType: '',
  }

  describe('rendering', () => {
    it('should render when visible is true', () => {
      const wrapper = mount(PublishModal, {
        props: defaultProps,
      })

      expect(wrapper.find('.publish-modal').exists()).toBe(true)
      expect(wrapper.find('.publish-modal-content').exists()).toBe(true)
    })

    it('should not render when visible is false', () => {
      const wrapper = mount(PublishModal, {
        props: {
          ...defaultProps,
          visible: false,
        },
      })

      expect(wrapper.find('.publish-modal').exists()).toBe(false)
    })

    it('should render modal header', () => {
      const wrapper = mount(PublishModal, {
        props: defaultProps,
      })

      expect(wrapper.find('.publish-modal-header h2').text()).toContain('发布到平台')
    })

    it('should render platform select', () => {
      const wrapper = mount(PublishModal, {
        props: defaultProps,
      })

      const select = wrapper.find('select')
      expect(select.exists()).toBe(true)
      const options = select.findAll('option')
      expect(options).toHaveLength(3)
      expect(options[0].text()).toBe('CSDN')
      expect(options[1].text()).toBe('知乎')
      expect(options[2].text()).toBe('掘金')
    })

    it('should render cookie textarea', () => {
      const wrapper = mount(PublishModal, {
        props: defaultProps,
      })

      const textarea = wrapper.find('textarea')
      expect(textarea.exists()).toBe(true)
      expect(textarea.attributes('placeholder')).toContain('直接粘贴浏览器复制的 Cookie')
    })

    it('should render cookie warning', () => {
      const wrapper = mount(PublishModal, {
        props: defaultProps,
      })

      const warning = wrapper.find('.cookie-warning')
      expect(warning.exists()).toBe(true)
      expect(warning.text()).toContain('安全提示')
      expect(warning.text()).toContain('服务端不会存储您的 Cookie')
    })

    it('should render publish button', () => {
      const wrapper = mount(PublishModal, {
        props: defaultProps,
      })

      const button = wrapper.find('.publish-submit-btn')
      expect(button.exists()).toBe(true)
      expect(button.text()).toBe('立即发布')
    })
  })

  describe('platform selection', () => {
    it('should display selected platform', () => {
      const wrapper = mount(PublishModal, {
        props: {
          ...defaultProps,
          platform: 'zhihu',
        },
      })

      const select = wrapper.find('select')
      expect(select.element.value).toBe('zhihu')
    })

    it('should emit update:platform when platform is changed', async () => {
      const wrapper = mount(PublishModal, {
        props: defaultProps,
      })

      const select = wrapper.find('select')
      await select.setValue('juejin')

      expect(wrapper.emitted('update:platform')).toBeTruthy()
      expect(wrapper.emitted('update:platform')?.[0]).toEqual(['juejin'])
    })
  })

  describe('cookie input', () => {
    it('should display cookie value', () => {
      const wrapper = mount(PublishModal, {
        props: {
          ...defaultProps,
          cookie: 'test=cookie; session=123',
        },
      })

      const textarea = wrapper.find('textarea')
      expect(textarea.element.value).toBe('test=cookie; session=123')
    })

    it('should emit update:cookie when cookie is changed', async () => {
      const wrapper = mount(PublishModal, {
        props: defaultProps,
      })

      const textarea = wrapper.find('textarea')
      await textarea.setValue('new=cookie')

      expect(wrapper.emitted('update:cookie')).toBeTruthy()
      expect(wrapper.emitted('update:cookie')?.[0]).toEqual(['new=cookie'])
    })
  })

  describe('help toggle', () => {
    it('should not show help by default', () => {
      const wrapper = mount(PublishModal, {
        props: defaultProps,
      })

      expect(wrapper.find('.cookie-help').exists()).toBe(false)
    })

    it('should show help when help link is clicked', async () => {
      const wrapper = mount(PublishModal, {
        props: defaultProps,
      })

      const helpLink = wrapper.find('.form-item label a')
      await helpLink.trigger('click')

      expect(wrapper.find('.cookie-help').exists()).toBe(true)
      expect(wrapper.find('.cookie-help').text()).toContain('获取 Cookie 步骤')
    })

    it('should hide help when help link is clicked again', async () => {
      const wrapper = mount(PublishModal, {
        props: defaultProps,
      })

      const helpLink = wrapper.find('.form-item label a')
      await helpLink.trigger('click')
      expect(wrapper.find('.cookie-help').exists()).toBe(true)

      await helpLink.trigger('click')
      expect(wrapper.find('.cookie-help').exists()).toBe(false)
    })
  })

  describe('publish button', () => {
    it('should be disabled when cookie is empty', () => {
      const wrapper = mount(PublishModal, {
        props: {
          ...defaultProps,
          cookie: '',
        },
      })

      const button = wrapper.find('.publish-submit-btn')
      expect(button.attributes('disabled')).toBeDefined()
    })

    it('should be disabled when cookie is only whitespace', () => {
      const wrapper = mount(PublishModal, {
        props: {
          ...defaultProps,
          cookie: '   ',
        },
      })

      const button = wrapper.find('.publish-submit-btn')
      expect(button.attributes('disabled')).toBeDefined()
    })

    it('should be disabled when publishing', () => {
      const wrapper = mount(PublishModal, {
        props: {
          ...defaultProps,
          cookie: 'test=cookie',
          isPublishing: true,
        },
      })

      const button = wrapper.find('.publish-submit-btn')
      expect(button.attributes('disabled')).toBeDefined()
    })

    it('should be enabled when cookie is valid and not publishing', () => {
      const wrapper = mount(PublishModal, {
        props: {
          ...defaultProps,
          cookie: 'test=cookie',
          isPublishing: false,
        },
      })

      const button = wrapper.find('.publish-submit-btn')
      expect(button.attributes('disabled')).toBeUndefined()
    })

    it('should show loading text when publishing', () => {
      const wrapper = mount(PublishModal, {
        props: {
          ...defaultProps,
          cookie: 'test=cookie',
          isPublishing: true,
        },
      })

      const button = wrapper.find('.publish-submit-btn')
      expect(button.text()).toBe('发布中...')
    })

    it('should show loading spinner when publishing', () => {
      const wrapper = mount(PublishModal, {
        props: {
          ...defaultProps,
          cookie: 'test=cookie',
          isPublishing: true,
        },
      })

      expect(wrapper.find('.spin').exists()).toBe(true)
    })

    it('should emit publish when clicked', async () => {
      const wrapper = mount(PublishModal, {
        props: {
          ...defaultProps,
          cookie: 'test=cookie',
        },
      })

      const button = wrapper.find('.publish-submit-btn')
      await button.trigger('click')

      expect(wrapper.emitted('publish')).toBeTruthy()
    })

    it('should not emit publish when cookie is empty', async () => {
      const wrapper = mount(PublishModal, {
        props: {
          ...defaultProps,
          cookie: '',
        },
      })

      const button = wrapper.find('.publish-submit-btn')
      await button.trigger('click')

      expect(wrapper.emitted('publish')).toBeFalsy()
    })

    it('should not emit publish when already publishing', async () => {
      const wrapper = mount(PublishModal, {
        props: {
          ...defaultProps,
          cookie: 'test=cookie',
          isPublishing: true,
        },
      })

      const button = wrapper.find('.publish-submit-btn')
      await button.trigger('click')

      expect(wrapper.emitted('publish')).toBeFalsy()
    })
  })

  describe('status display', () => {
    it('should not show status by default', () => {
      const wrapper = mount(PublishModal, {
        props: defaultProps,
      })

      expect(wrapper.find('.publish-status').exists()).toBe(false)
    })

    it('should show success status', () => {
      const wrapper = mount(PublishModal, {
        props: {
          ...defaultProps,
          status: '发布成功！',
          statusType: 'success',
        },
      })

      const status = wrapper.find('.publish-status')
      expect(status.exists()).toBe(true)
      expect(status.text()).toBe('发布成功！')
      expect(status.classes()).toContain('success')
    })

    it('should show error status', () => {
      const wrapper = mount(PublishModal, {
        props: {
          ...defaultProps,
          status: '发布失败，请检查 Cookie',
          statusType: 'error',
        },
      })

      const status = wrapper.find('.publish-status')
      expect(status.exists()).toBe(true)
      expect(status.text()).toBe('发布失败，请检查 Cookie')
      expect(status.classes()).toContain('error')
    })

    it('should show info status', () => {
      const wrapper = mount(PublishModal, {
        props: {
          ...defaultProps,
          status: '正在准备发布...',
          statusType: 'info',
        },
      })

      const status = wrapper.find('.publish-status')
      expect(status.exists()).toBe(true)
      expect(status.text()).toBe('正在准备发布...')
      expect(status.classes()).toContain('info')
    })
  })

  describe('modal close', () => {
    it('should emit close when close button is clicked', async () => {
      const wrapper = mount(PublishModal, {
        props: defaultProps,
      })

      const closeButton = wrapper.find('.publish-modal-header button')
      await closeButton.trigger('click')

      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('should emit close when clicking outside modal content', async () => {
      const wrapper = mount(PublishModal, {
        props: defaultProps,
      })

      const modal = wrapper.find('.publish-modal')
      await modal.trigger('click')

      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('should not emit close when clicking inside modal content', async () => {
      const wrapper = mount(PublishModal, {
        props: defaultProps,
      })

      const modalContent = wrapper.find('.publish-modal-content')
      await modalContent.trigger('click')

      expect(wrapper.emitted('close')).toBeFalsy()
    })
  })
})
