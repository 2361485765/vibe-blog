"""
小红书内容生成服务

复用现有服务：
- PromptManager: 模板渲染
- NanoBananaService: 图片生成
- VideoService: 动画生成
- OSSService: 文件上传
- LLMService: 文本生成
"""

import re
import json
import logging
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class XHSPage:
    """小红书页面"""
    index: int
    page_type: str  # cover, content, summary
    content: str


@dataclass
class XHSGenerateResult:
    """小红书生成结果"""
    topic: str
    style: str
    pages: List[XHSPage] = field(default_factory=list)
    image_urls: List[str] = field(default_factory=list)
    video_url: Optional[str] = None
    titles: List[str] = field(default_factory=list)
    copywriting: str = ""
    tags: List[str] = field(default_factory=list)
    outline: str = ""


class XHSService:
    """小红书内容生成服务"""
    
    def __init__(
        self,
        llm_client,
        image_service=None,
        video_service=None,
        oss_service=None
    ):
        """
        初始化小红书服务
        
        Args:
            llm_client: LLM 客户端
            image_service: 图片生成服务（NanoBananaService）
            video_service: 视频生成服务
            oss_service: OSS 服务
        """
        self.llm = llm_client
        self.image_service = image_service
        self.video_service = video_service
        self.oss_service = oss_service
        
        # 导入 PromptManager
        from services.blog_generator.prompts.prompt_manager import get_prompt_manager
        self.prompt_manager = get_prompt_manager()
        
        logger.info("XHSService 初始化完成")
    
    async def generate_series(
        self,
        topic: str,
        count: int = 4,
        style: str = "hand_drawn",
        content: str = None,
        generate_video: bool = True
    ) -> XHSGenerateResult:
        """
        生成完整的小红书系列
        
        Args:
            topic: 主题
            count: 页面数量（包括封面）
            style: 风格（hand_drawn/claymation）
            content: 参考内容（可选）
            generate_video: 是否生成动画封面
            
        Returns:
            XHSGenerateResult
        """
        logger.info(f"开始生成小红书系列: topic={topic}, count={count}, style={style}")
        
        result = XHSGenerateResult(topic=topic, style=style)
        
        # Step 1: 生成大纲
        logger.info("Step 1: 生成大纲...")
        outline, pages = await self._generate_outline(topic, count, content)
        result.outline = outline
        result.pages = pages
        logger.info(f"大纲生成完成，共 {len(pages)} 页")
        
        # Step 2: 并行生成所有图片 + 文案
        logger.info("Step 2: 并行生成所有图片和文案...")
        
        # 创建所有图片生成任务
        image_tasks = []
        for i, page in enumerate(pages):
            image_tasks.append(self._generate_single_image(
                page, style, topic, outline, is_first=(i == 0)
            ))
        
        # 文案生成任务
        content_task = self._generate_content(topic, outline)
        
        # 并行执行所有图片生成 + 文案生成
        all_results = await asyncio.gather(*image_tasks, content_task)
        
        # 分离结果：前 N 个是图片，最后一个是文案
        image_urls = [url for url in all_results[:-1] if url]
        content_result = all_results[-1]
        
        logger.info(f"并行生成完成: {len(image_urls)} 张图片")
        
        # Step 3: 生成动画封面（需要封面图完成后）
        video_url = None
        if generate_video and image_urls:
            logger.info("Step 3: 生成动画封面...")
            video_url = await self._generate_video(image_urls[0])
        
        result.image_urls = image_urls
        result.video_url = video_url
        result.titles = content_result.get('titles', [])
        result.copywriting = content_result.get('copywriting', '')
        result.tags = content_result.get('tags', [])
        
        logger.info(f"小红书系列生成完成: {len(result.image_urls)} 张图片, 视频={result.video_url is not None}")
        return result
    
    async def _async_return(self, value):
        """辅助方法：返回一个异步值"""
        return value
    
    async def _generate_outline(
        self,
        topic: str,
        count: int,
        content: str = None
    ) -> tuple:
        """
        生成大纲
        
        Returns:
            (outline_text, pages_list)
        """
        prompt = self.prompt_manager.render_xhs_outline(
            topic=topic,
            count=count,
            content=content
        )
        
        # 调用 LLM 生成大纲
        outline_text = self._call_llm_sync(prompt)
        
        # 解析大纲
        pages = self._parse_outline(outline_text)
        
        return outline_text, pages
    
    def _parse_outline(self, outline_text: str) -> List[XHSPage]:
        """解析大纲文本为页面列表"""
        # 按 <page> 分割页面
        if '<page>' in outline_text.lower():
            pages_raw = re.split(r'<page>', outline_text, flags=re.IGNORECASE)
        else:
            # 向后兼容：如果没有 <page> 则使用 ---
            pages_raw = outline_text.split("---")
        
        pages = []
        for index, page_text in enumerate(pages_raw):
            page_text = page_text.strip()
            if not page_text:
                continue
            
            # 解析页面类型
            page_type = "content"
            type_match = re.match(r"\[(\S+)\]", page_text)
            if type_match:
                type_cn = type_match.group(1)
                type_mapping = {
                    "封面": "cover",
                    "内容": "content",
                    "总结": "summary",
                }
                page_type = type_mapping.get(type_cn, "content")
            
            pages.append(XHSPage(
                index=len(pages),
                page_type=page_type,
                content=page_text
            ))
        
        return pages
    
    async def _generate_single_image(
        self,
        page: XHSPage,
        style: str,
        topic: str,
        outline: str,
        is_first: bool = False
    ) -> Optional[str]:
        """生成单张图片"""
        if not self.image_service or not page:
            return None
        
        from services.image_service import AspectRatio
        
        logger.info(f"生成图片: {page.page_type} (index={page.index})")
        
        # 第一步：生成 LLM Prompt（用于 ghibli_summer 两步法）
        llm_prompt = self.prompt_manager.render_xhs_image(
            page_content=page.content,
            page_type=page.page_type,
            style=style,
            reference_image=not is_first,
            user_topic=topic,
            full_outline=outline,
            page_index=page.index
        )
        
        # 两步法：ghibli_summer 风格需要先用 LLM 生成视觉 Prompt
        if style == 'ghibli_summer':
            logger.info(f"[两步法] Step 1: LLM 生成视觉 Prompt...")
            visual_prompt = self._call_llm_sync(llm_prompt)
            logger.info(f"[两步法] Step 2: 使用视觉 Prompt 生成图片...")
            prompt = visual_prompt
        else:
            prompt = llm_prompt
        
        result = self.image_service.generate(
            prompt=prompt,
            aspect_ratio=AspectRatio.PORTRAIT_3_4,
            download=True
        )
        
        if result and result.oss_url:
            return result.oss_url
        elif result and result.url:
            return result.url
        return None
    
    async def _generate_remaining_images(
        self,
        pages: List[XHSPage],
        style: str,
        topic: str,
        outline: str
    ) -> List[str]:
        """生成剩余图片（封面之后的图片）"""
        if not self.image_service or not pages:
            return []
        
        image_urls = []
        for i, page in enumerate(pages):
            logger.info(f"生成第 {i+2}/{len(pages)+1} 张图片: {page.page_type}")
            url = await self._generate_single_image(page, style, topic, outline, is_first=False)
            if url:
                image_urls.append(url)
            else:
                logger.error(f"第 {i+2} 张图片生成失败")
        
        return image_urls
    
    async def _generate_images(
        self,
        pages: List[XHSPage],
        style: str,
        topic: str,
        outline: str
    ) -> List[str]:
        """生成图片（保留用于兼容）"""
        if not self.image_service:
            logger.warning("图片服务未配置，跳过图片生成")
            return []
        
        from services.image_service import AspectRatio
        
        image_urls = []
        reference_image = None
        
        for i, page in enumerate(pages):
            logger.info(f"生成第 {i+1}/{len(pages)} 张图片: {page.page_type}")
            
            # 渲染图片生成 Prompt
            prompt = self.prompt_manager.render_xhs_image(
                page_content=page.content,
                page_type=page.page_type,
                style=style,
                reference_image=(reference_image is not None),
                user_topic=topic,
                full_outline=outline
            )
            
            # 生成图片
            result = self.image_service.generate(
                prompt=prompt,
                aspect_ratio=AspectRatio.PORTRAIT_3_4,  # 3:4 竖版
                download=True
            )
            
            if result and result.oss_url:
                image_urls.append(result.oss_url)
                # 第一张图作为后续的参考（风格一致性）
                if i == 0:
                    reference_image = result.oss_url
            elif result and result.url:
                image_urls.append(result.url)
                if i == 0:
                    reference_image = result.url
            else:
                logger.error(f"第 {i+1} 张图片生成失败")
        
        return image_urls
    
    async def _generate_video(self, cover_image_url: str) -> Optional[str]:
        """生成动画封面"""
        if not self.video_service:
            logger.warning("视频服务未配置，跳过动画生成")
            return None
        
        try:
            # 使用现有的封面视频生成 Prompt
            video_prompt = self.prompt_manager.render_cover_video_prompt()
            
            # 调用视频服务（同步方法，在线程中执行）
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.video_service.generate_from_image(
                    image_url=cover_image_url,
                    prompt=video_prompt
                )
            )
            
            video_url = result.oss_url if result and result.oss_url else (result.url if result else None)
            
            return video_url
        except Exception as e:
            logger.error(f"动画生成失败: {e}")
            return None
    
    async def _generate_content(self, topic: str, outline: str) -> Dict[str, Any]:
        """生成小红书文案"""
        prompt = self.prompt_manager.render_xhs_content(
            topic=topic,
            outline=outline
        )
        
        # 调用 LLM 生成文案
        response = self._call_llm_sync(prompt)
        
        # 解析 JSON 响应
        try:
            # 提取 JSON 部分
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response
            
            result = json.loads(json_str)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"解析文案 JSON 失败: {e}")
            return {
                'titles': [topic],
                'copywriting': response,
                'tags': []
            }
    
    def _call_llm_sync(self, prompt: str, json_format: bool = False) -> str:
        """
        同步调用 LLM（统一使用 LLMService 标准接口）
        
        Args:
            prompt: 提示词
            json_format: 是否要求 JSON 格式响应
        """
        response = self.llm.chat(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"} if json_format else None
        )
        
        if response is None:
            raise Exception("LLM 返回空响应")
        
        return response


# 全局实例
_xhs_service: Optional[XHSService] = None


def init_xhs_service(
    llm_client,
    image_service=None,
    video_service=None,
    oss_service=None
) -> XHSService:
    """初始化小红书服务"""
    global _xhs_service
    _xhs_service = XHSService(
        llm_client=llm_client,
        image_service=image_service,
        video_service=video_service,
        oss_service=oss_service
    )
    return _xhs_service


def get_xhs_service() -> Optional[XHSService]:
    """获取小红书服务实例"""
    return _xhs_service
