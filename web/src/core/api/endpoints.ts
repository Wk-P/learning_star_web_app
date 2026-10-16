/**
 * 两个后端在同一域名下的入口（nginx / vite 代理负责去掉前缀转发）：
 *   /api/topik/*  → topik 后端 :8000/api/*   账号、登录、视频/音频/文件、权限
 *   /api/course/* → course 后端 :8001/api/*  科目、B 站链接、路线图
 * 登录只在 topik 后端完成，course 后端用同一密钥校验 topik 签发的令牌。
 */
export const TOPIK_API = '/api/topik'
export const COURSE_API = '/api/course'
