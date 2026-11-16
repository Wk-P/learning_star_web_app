/**
 * 后端只有一个（Django，backend/），nginx / vite 代理把 /api、/media 转发过去：
 *   /api/auth/*       登录、刷新令牌
 *   /api/accounts/*   我的账户、用户管理
 *   /api/languages/*  语言学习：分类与语言、视频/音频/资料、学习权限
 *   /api/courses/*    课程：科目与视频链接
 */
export const API = '/api'
