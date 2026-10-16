# frontend
本项目是前端

递进层级使用面包屑展示


## 路由守卫
**路由守卫1**：用户是否登录

## 状态查询
[pinia]
**用户-课程关联状态**：用户是否申请该课程

## 时间检查
**每个请求开始前后都需要进行时间检查**：检查用户的UTC时间

- 以下标注【路由守卫】和【状态查询】的界面逻辑叙述，默认表示用户已经登录、已经申请课程

## 页面中间状态/页面其他响应状态
- 空数据则显示对应【xxx为空...】
- 错误直接跳转自定义error界面，error界面给出链接跳转首页
- api请求失败根据 status-code 定义前端消息，给出自定义 alert 窗口（或者el-plus组件）

## Layout
### HomeLayout
【路由守卫】
【状态查询】
显示主要界面的操作功能
主要是 head nav 和 footer
#### head nav
【课程列表】
【用户界面/{username}替换】


### UserLayout
【路由守卫】
1. 侧边栏显示【修改密码】，【我的课程】，【我的作业】，【我的成绩】   
- 【我的课程】UserCourseListView：显示所有已经申请的课程列表，列表item文案是课程名称，都是链接，课程链接会跳转到课程主界面
- 【我的作业】UserHomeworkListView：显示各科当周正在进行作业，以及历史作业列表。点击对应作业会跳转到作业主界面
- 【我的成绩】UserScoreView：点击之后跳转成绩界面，查看各个课程最终成绩评分。如果课程没有结束，则显示正在进行的课程。


### UserProfileView
【路由守卫】
【状态查询】
配合UserLayout + 用户基本状态显示

### UserCourseView
用户已经申请的课程列表，使用 grid card 布局展示粗略信息
如果点击课程链接则进入对应的 CourseView 界面

### User


### HomeView
【路由守卫】
【状态查询】
这是用户登录后的主界面，利用grid视图显示
- 用户正在进行的课程
- 用户已经完成的课程
- 用户还未开始的课程


### CourseListView
【路由守卫】
【状态查询】
这是给用户进行第一步，分科展示的地方，就是分科目录，只用 grid card 模式展示所有的课程分科，而不是课程单元章节。本界面会读取后端，检查用户和课程状态；并且对于每个 card，进行以下展示
1. 课程状态
- 未开始
- 进行中
- 已结束

2. 用户状态
- 未申请 
  - 课程：未开始、进行中、已结束
- 已申请
  - 课程：未开始、进行中、已结束

3. 链接按钮
- - 如果【已申请-已结束】，可以添加链接显示【查看课程】和【查询成绩】；如果【已申请-进行中】，链接则是【查看课程】、【查看作业】；如果【已申请-未开始】，则链接只有【查看课程】
- - 如果【未申请-x】，则链接只展示【查看课程】


### CourseView [route query: courseId]
【路由守卫】
【状态查询】
这是当用户在 CourseListView 点击 Course Card 中课程详情之后跳转的界面。课程包含内容
1. title/课程名称
2. 课程描述
3. 课程状态【未开始、已开始、已结束】
4. 对于用户状态：【可加入、不可加入】
5. 课程时间表和作业时间表
- 【课程时间表】：列出 ClassView 的链接 + title + 上课时间【YYYY-MM-DD HH:MM】，例如：【CourseName】第n周第m课。
- 【作业时间表】：当用户已经申请该课程，则显示在当前周期内进行的作业和过往作业，不显示未开启作业；如果用户没有申请，只显示当期作业。
6. 【随堂作业】：如果用户已经加入且课程已开始，则显示改按钮；其余情况都不显示该按钮。



### ClassView [route query: courseId, classId]
【路由守卫】
【状态查询】
这是用户在 CourseView 点击（某周某节）课链接后进入的界面，展示内容如下
1. 这节课上课时间【YYYY-MM-DD HHM:MM】
- 显示远程课程的会议室链接，如果在期限内，则显示为链接（可用），否则禁用链接显示【已过期】
2. 讲课人姓名，学生列表。
3. 当前这节课使用的文件：讲义或者作业等资料文件
4. 作业按钮
- 如果用户已经申请，则显示【本周作业】链接到对应作业
- 如果用户未申请，不显示按钮


### HomeworkView
【路由守卫】
【状态查询】
这是用户点击具体某个作业链接展示的详情界面
1. 作业对应的课程
2. 作业状态：
- 和用户状态挂钩，用户是否申请课程，用户是否已经提交作业
状态显示：未提交/已提交；如果正在当期：显示【提交/重新提交】按钮；已经过期：【查看评分】按钮。
- 没申请无法进入此页
- 课程如果已经结束，则直接显示作业评分状态和评分值：如果已评分，显示【已评分，{评分值}/100】；否则显示【未评分，--/100】。


作业提交类型：pdf/docx/docs 文件、截图、代码文件等，不超过 50MB；期限内允许重复提交


## AdminLayout
Head nav 或者 侧边烂具备【用户管理】【课程管理】【作业管理】【分数管理】的工具栏

在叙述管理员功能之前，先给出用户身份
1. 学生 student - user 
2. 教师 teacher - staff
3. 管理员 admin - admin   


管理员界面包含全量信息，并且包含所有的修改权限。
管理员权限：
- 账户信息管理
  1. 用户名（登录ID）增删改查，重置用户密码，生成随机新密码
  2. 用户课程管理及所属作业管理
  - 用户课程管理：删除，添加，改时间
  - 用户作业管理：浏览提交的作业文件，评分。
- 课程信息管理
  1. 课程名称
  2. 课程时间：开始时间，结束时间
  3. 课程时间制度
  4. 课程描述
  5. 课程文件管理
  6. 课程分数设置
  7. 出勤表管理
- 作业信息管理
  1. 作业对应课程
  2. 作业名称
  3. 作业描述
  4. 作业时间：开始时间，结束时间
  5. 作业分数设置


教师权限
- 无权操作用户
- 有权进行课程信息管理和作业信息管理


学生权限
- 仅支持对作业进行提交的修改
- 其余均为查看权限



### AdminHomeView
显示Dashboard信息和基础便捷按钮，和 AdminLayout 重复没关系，grid 显示


### AdminUserControlView
用户管理：用户身份管理，用户名，密码修改。子路由如下
- AdminUserCourseListControlView
  
  管理某个用户所申请的课程列表信息，不同课程不同颜色显示

- AdminUserCourseControlView

  管理某个用户具体一个课程的信息

- AdminUserClassControlView

  管理某个用户具体某一天课程的信息

- AdminUserHomeworkListControlView

  管理某个用户所有的作业列表信息，不同课程不同颜色显示

- AdminUserHomeworkControlView
 
  管理某个用户单个作业信息

### AdminCourseControlView
针对课程本身信息进行控制

### AdminClassControlView
针对某个学科课程的某一节课进行细致控制

### AdminHomeworkListView
不同颜色表示不同学科/课程，展示控制全量作业列表

### AdminHomeworkView
详细控制某一个课程的某一周作业

## UX 调用层级
AppView: {
  UserLayout: [
    UserProfileView, UserCourseListView, UserHomeworkListView, UserScoresView, HomeworkView
  ],
  HomeLayout: [
    HomeView, CourseListView, CourseView, ClassView
  ],
  AdminLayout: [
    AdminView, AdminUserProfileControllView, AdminUserCourseControlView, AdminUserHomeworkControlView, ...
  ]
}

HomeLayout 的 head nav 有 UserLayout 的链接
UserLayout 的 head nav 有 HomeLayout 的链接