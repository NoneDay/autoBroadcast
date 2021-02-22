CREATE TABLE [dbo].[zhanbao_tbl](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[worker_no] [nvarchar](max) NULL,
	[report_name] [nvarchar](255) NULL,
	[config_txt] [nvarchar](max) NULL,
	[cron_str] [nvarchar](255) NULL,
	[cron_start] [tinyint] NULL,
	[text_template] [nvarchar](max) NULL,
	[result] [nvarchar](max) NULL,
	[pid] [int] NULL,
	[xuhao] [int] NULL,
	[is_catalog] [bit] NULL,
 CONSTRAINT [PK_zhanbao_tbl] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

ALTER TABLE [dbo].[zhanbao_tbl] ADD  DEFAULT ((0)) FOR [is_catalog]


-- ----------------------------
-- Table structure for login_tbl
-- ----------------------------
IF EXISTS (SELECT * FROM sys.all_objects WHERE object_id = OBJECT_ID(N'[dbo].[login_tbl]') AND type IN ('U'))
	DROP TABLE [dbo].[login_tbl]
GO

CREATE TABLE [dbo].[login_tbl] (
  [id] int  IDENTITY(1,1) NOT NULL,
  [worker_no] nvarchar(20) COLLATE Chinese_PRC_CI_AS  NOT NULL,
  [sys_name] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NOT NULL,
  [username] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NOT NULL,
  [password] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NOT NULL
)
GO

ALTER TABLE [dbo].[login_tbl] SET (LOCK_ESCALATION = TABLE)
GO


-- ----------------------------
-- Records of [login_tbl]
-- ----------------------------
SET IDENTITY_INSERT [dbo].[login_tbl] ON
GO

GO

SET IDENTITY_INSERT [dbo].[login_tbl] OFF
GO


-- ----------------------------
-- Table structure for sys_register
-- ----------------------------
IF EXISTS (SELECT * FROM sys.all_objects WHERE object_id = OBJECT_ID(N'[dbo].[sys_register]') AND type IN ('U'))
	DROP TABLE [dbo].[sys_register]
GO

CREATE TABLE [dbo].[sys_register] (
  [id] int  IDENTITY(1,1) NOT NULL,
  [worker_no] varchar(50) COLLATE Chinese_PRC_CI_AS  NULL,
  [name] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NULL,
  [type] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NULL,
  [json_txt] nvarchar(max) COLLATE Chinese_PRC_CI_AS  NULL
)
GO

ALTER TABLE [dbo].[sys_register] SET (LOCK_ESCALATION = TABLE)
GO


-- ----------------------------
-- Records of [sys_register]
-- ----------------------------
SET IDENTITY_INSERT [dbo].[sys_register] ON
GO

INSERT INTO [dbo].[sys_register] ([id], [worker_no], [name], [type], [json_txt]) VALUES (N'3', N'14100298', N'河南通用', N'河南', N'{"name": "河南通用", "type": "河南", "patterns": ["http://"], "allow_userid": "^[1|A]41.+", "login_data_type": "form", "login_url": "", "login_data_template": {"qwe": "qweqw"}, "login_success": "", "login_error": "", "headers": {}, "next_headers": {"needType": "json", "worker_no": "{{userid}}"}, "next_cookies": {}, "id": 3, "json_txt": {"name": "qweqwe", "type": "qweqwe", "patterns": ["qweqw"], "allow_userid": "", "login_data_type": "form", "login_url": "", "login_data_template": [{"prop": "qwe", "value": "qweqw", "$index": 0, "$cellEdit": true}], "login_success": "", "login_error": "", "headers": [], "next_headers": [], "next_cookies": [{"$cellEdit": true, "$index": 0, "prop": "ff", "value": "ff"}], "$login_data_type": "form", "id": 3}, "$login_data_type": "form", "$index": 0, "$type": "河南"}')
GO

INSERT INTO [dbo].[sys_register] ([id], [worker_no], [name], [type], [json_txt]) VALUES (N'4', N'14100298', N'河南个险331', N'河南', N'{"name": "河南个险331", "type": "河南", "patterns": ["http://report.hn.clic/report3/zdjy.aspx"], "allow_userid": "^[1|A]41.+", "login_data_type": "form", "login_url": "http://report.hn.clic/gxzc_331/home/login", "login_data_template": {"emp.empNo": "{{username}}", "emp.empPassword": "{{password}}"}, "login_success": "", "login_error": "用户名或密码错误", "headers": {}, "next_headers": {"needType": "json", "worker_no": "{{username}}"}, "next_cookies": {}, "id": 4, "json_txt": {"name": "河南个险331", "type": "河南", "patterns": ["http://report.hn.clic/report3/zdjy.aspx"], "allow_userid": "^141.+", "login_data_type": "form", "login_url": "http://report.hn.clic/gxzc_331/home/login", "login_data_template": [{"prop": "emp.empNo", "value": "{{username}}", "$index": 0, "$cellEdit": true}, {"prop": "emp.empPassword", "value": "{{password}}", "$index": 1, "$cellEdit": true}], "login_success": "", "login_error": "用户名或密码错误", "headers": [], "next_headers": [{"prop": "needType", "value": "json", "$index": 0, "$cellEdit": true}, {"prop": "worker_no", "value": "{{username}}", "$index": 1, "$cellEdit": true}], "next_cookies": [], "$login_data_type": "form", "id": 4}, "worker_no": "14100298", "$login_data_type": "form", "$index": 1, "$type": "河南"}')
GO

INSERT INTO [dbo].[sys_register] ([id], [worker_no], [name], [type], [json_txt]) VALUES (N'5', N'14100298', N'帆软demo', N'帆软', N'{"name": "帆软demo","proxy":"http://10.20.112.145:8080", "type": "帆软", "patterns": ["http://demo.finereport.com/decision/"], "allow_userid": ".*", "login_data_type": "json", "login_url": "http://demo.finereport.com/decision/login", "login_data_template": {"username": "{{username}}", "password": "{{password}}", "validity": "-1", "encrypted": "false"}, "login_success": "", "login_error": "errorCode", "headers": {"Accept": "application/json, text/javascript, */*; q=0.01", "Cookie": "fine_remember_login=-1", "X-Requested-With": "XMLHttpRequest"}, "next_headers": {"Authorization": "Bearer {{login_data[\"data\"][\"accessToken\"]}}"}, "next_cookies": {"fine_remember_login": "-1", "fine_auth_token": "{{login_data[\"data\"][\"accessToken\"]}}"}, "id": 5, "json_txt": {"name": "帆软", "type": "帆软", "patterns": ["http://demo.finereport.com/decision/"], "allow_userid": ".*", "login_data_type": "json", "login_url": "http://demo.finereport.com/decision/login", "login_data_template": [{"prop": "username", "value": "{{username}}", "$index": 0, "$cellEdit": true}, {"prop": "password", "value": "{{password}}", "$index": 1, "$cellEdit": true}, {"prop": "validity", "value": "-1", "$index": 2, "$cellEdit": true}, {"prop": "encrypted", "value": "false", "$index": 3, "$cellEdit": true}], "login_success": "", "login_error": "errorCode", "headers": [{"prop": "Accept", "value": "application/json, text/javascript, */*; q=0.01", "$index": 0, "$cellEdit": true}, {"prop": "Cookie", "value": "fine_remember_login=-1", "$index": 1, "$cellEdit": true}, {"prop": "X-Requested-With", "value": "XMLHttpRequest", "$index": 2, "$cellEdit": true}], "next_headers": [{"prop": "Authorization", "value": "Bearer {{login_data[\"data\"][\"accessToken\"]}}", "$index": 0, "$cellEdit": true}], "next_cookies": [{"prop": "fine_remember_login", "value": "-1", "$index": 0, "$cellEdit": true}, {"prop": "fine_auth_token", "value": "{{login_data[\"data\"][\"accessToken\"]}}", "$index": 1, "$cellEdit": true}], "$login_data_type": "json", "id": 5}, "$login_data_type": "json", "$index": 2}')
GO

INSERT INTO [dbo].[sys_register] ([id], [worker_no], [name], [type], [json_txt]) VALUES (N'14', N'14100298', N'总部DM', N'帆软', N'{"name": "总部DM", "type": "帆软", "patterns": ["http://10.249.2.11:8080/webroot/decision/"], "allow_userid": ".*", "login_data_type": "json", "login_url": "http://10.249.2.11:8080/webroot/decision/login", "login_data_template": {"username": "{{username}}", "password": "{{password}}", "validity": "-1", "encrypted": "false"}, "login_success": "", "login_error": "errorCode", "headers": {"Accept": "application/json, text/javascript, */*; q=0.01", "Cookie": "fine_remember_login=-1", "X-Requested-With": "XMLHttpRequest"}, "next_headers": {"Authorization": "Bearer {{login_data[\"data\"][\"accessToken\"]}}"}, "next_cookies": {"fine_remember_login": "-1", "fine_auth_token": "{{login_data[\"data\"][\"accessToken\"]}}"}, "id": 14, "json_txt": {"name": "总部DM", "type": "帆软", "patterns": ["http://demo.finereport.com/decision/"], "allow_userid": ".*", "login_data_type": "json", "login_url": "http://demo.finereport.com/decision/login", "login_data_template": [{"prop": "username", "value": "{{username}}", "$index": 0, "$cellEdit": true}, {"prop": "password", "value": "{{password}}", "$index": 1, "$cellEdit": true}, {"prop": "validity", "value": "-1", "$index": 2, "$cellEdit": true}, {"prop": "encrypted", "value": "false", "$index": 3, "$cellEdit": true}], "login_success": "", "login_error": "errorCode", "headers": [{"prop": "Accept", "value": "application/json, text/javascript, */*; q=0.01", "$index": 0, "$cellEdit": true}, {"prop": "Cookie", "value": "fine_remember_login=-1", "$index": 1, "$cellEdit": true}, {"prop": "X-Requested-With", "value": "XMLHttpRequest", "$index": 2, "$cellEdit": true}], "next_headers": [{"prop": "Authorization", "value": "Bearer {{login_data[\"data\"][\"accessToken\"]}}", "$index": 0, "$cellEdit": true}], "next_cookies": [{"prop": "fine_remember_login", "value": "-1", "$index": 0, "$cellEdit": true}, {"prop": "fine_auth_token", "value": "{{login_data[\"data\"][\"accessToken\"]}}", "$index": 1, "$cellEdit": true}], "$login_data_type": "json", "id": 5}, "$login_data_type": "json", "$index": 3, "$type": "帆软"}')
GO

SET IDENTITY_INSERT [dbo].[sys_register] OFF
GO


-- ----------------------------
-- Indexes structure for table login_tbl
-- ----------------------------
CREATE NONCLUSTERED INDEX [idx_1]
ON [dbo].[login_tbl] (
  [worker_no] ASC,
  [sys_name] ASC
)
GO


-- ----------------------------
-- Primary Key structure for table login_tbl
-- ----------------------------
ALTER TABLE [dbo].[login_tbl] ADD CONSTRAINT [PK__login_tb__3213E83F690E5404] PRIMARY KEY CLUSTERED ([id])
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)  
ON [PRIMARY]
GO


-- ----------------------------
-- Indexes structure for table sys_register
-- ----------------------------
CREATE UNIQUE NONCLUSTERED INDEX [IX_sys_register]
ON [dbo].[sys_register] (
  [name] ASC
)
GO


-- ----------------------------
-- Primary Key structure for table sys_register
-- ----------------------------
ALTER TABLE [dbo].[sys_register] ADD CONSTRAINT [PK_sys_register] PRIMARY KEY CLUSTERED ([id])
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)  
ON [PRIMARY]
GO

