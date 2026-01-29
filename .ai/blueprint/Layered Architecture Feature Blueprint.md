蓝图名称：API优先开发蓝图 (API-First Development Blueprint)
版本: 3.0
作者: 编码助手 (AI)
描述: 本蓝图专为“API优先”开发流程设计。你提供已定义好的ApiService接口和DTO数据类，我将自动解析这些代码，并为你生成完成剩余所有层级（Domain, Data层实现, Presentation）所需的、完整的开发任务清单。

第一部分：如何使用本蓝图 (你的输入)
当你完成了API接口和DTO的定义后，请复制并填写下方的《API优先开发需求表》，然后将其提供给我。

# API优先开发需求表

## 1. 功能名称 (Feature Name):
[例如：创建红包]

## 2. 功能模块路径 (Feature Module Path):
[在 presentation 层下的包名，例如：redpocket.create]

## 3. 表现层模式 (Presentation Layer Pattern):
[请选择一项: MVI / MVVM]

## 4. API服务接口代码 (ApiService Interface Code):
(请将定义好的 **Retrofit Service接口** 的完整代码粘贴在此处)
```kotlin
// 例如: com.example.data.remote.api.RedPocketApiService
interface RedPocketApiService {
    @GET("redpocket/config")
    suspend fun getConfig(): RedPocketConfigDto

    @POST("redpocket/create")
    suspend fun createRedPocket(@Body request: CreateRedPocketRequest): CreateRedPocketResponse
}
```
## 5. 数据传输对象代码 (DTO Code):
(请将相关的 DTO数据类 的完整代码粘贴在此处)

## 6. 成功/失败/业务行为 (Success/Failure/Business Logic):
关键业务规则: [例如：金额必须是正整数]
成功行为: [例如：导航到红包详情页]
失败行为: [例如：在当前页面显示一个Toast提示错误信息]

## 7. 已有复用组件 (Existing Reusable Components):
(如果你正在扩展一个已有的模块，请列出可能需要更新的文件)

Repository接口: [例如：RedPocketRepository.kt]
Mapper文件: [例如：RedPocketMapper.kt]

### **第二部分：任务生成蓝图 (AI的输出结构)**

AI将解析用户提供的代码，然后生成一份高度定制的任务清单。**已经知道`ApiService`和`DTO`的存在，所以不会再让创建它们**，而是直接进入下一步。

```markdown
# 任务清单：<功能名称> (基于API优先流程)

**分析摘要**: 已收到并解析 `...ApiService` 和相关DTOs。现在开始生成剩余任务。

## [ Domain Layer - 领域层 ]

- [ ] **1. 定义核心业务模型**
    - **位置**: `com.example.domain.model`
    - **文件**: `<核心实体名>.kt`, ...
    - **说明**: **基于已提供的DTO** (`<DTO文件名>.kt`), 创建对应的、无框架依赖的Domain模型。请注意处理好可空性与业务的默认值。

- [ ] **2. 定义/更新仓库接口**
    - **位置**: `com.example.domain.repository`
    - **文件**: `<核心实体名>Repository.kt`
    - **说明**: **基于 `...ApiService` 中的方法**，在仓库接口中创建或更新对应的抽象方法。参数和返回值应使用Domain模型。
        ```kotlin
        // 自动推断出的方法:
        suspend fun getConfig(): RedPocketConfig
        suspend fun createRedPocket(params: ...): ...
        ```

- [ ] **3. 定义业务用例**
    - **位置**: `com.example.domain.usecase`
    - **文件**: `...UseCase.kt`
    - **说明**: 为仓库接口中的每个方法创建独立的UseCase类，以封装业务逻辑。

## [ Data Layer - 数据层 ]

- [ ] **1. 创建/更新数据模型转换器 (Mapper)**
    - **位置**: `com.example.data.mapper`
    - **文件**: `<核心实体名>Mapper.kt`
    - **说明**: **创建或更新该文件**，以提供以下必要的转换函数：
        - `<DTO响应类>.toDomain()`
        - `<Domain请求参数类>.toRequest()` (如果需要)

- [ ] **2. 实现/更新仓库接口**
    - **位置**: `com.example.data.repository`
    - **文件**: `<核心实体名>RepositoryImpl.kt`
    - **说明**: **创建或更新该实现类**。注入你已定义的 `...ApiService` 和刚创建的 `...Mapper`。实现Domain层Repository接口中定义的所有方法。

## [ Presentation Layer - 表现层 (根据你的选择生成) ]

### **>>> 如果模式为 MVI / MVVM <<<**
---
- [ ] **1. 定义/实现 ViewModel**
    - **说明**: ...
- [ ] **2. 构建 UI 界面**
    - **说明**: ...

---