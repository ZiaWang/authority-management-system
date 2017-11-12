# authority-management-system

> RBAC(Role-based access control)，基于角色的权限管理系统

![PythonVersions](https://img.shields.io/badge/python%20-3.5%2B-blue.svg)
![DjangoVersions](https://img.shields.io/badge/Django%20-1.11%2B-green.svg)

## Introduction
### RBAC
- 所谓基于角色的权限管理，说白了就是用户通过角色来拥有相对应的权限，其与权限之间没有直接关系。如果知识单纯的将用户与权限直接关联起来，那么当用户的权限或者权限内容发生改变的时候，处理起来就显得非常的低效。主要有以下几点
	- 重复造轮子。每一个用户时，我们都需要将与其对应的权限一个个与其关联，同理，当新增加一个权限的时候，我们要将该权限一个个的添加到对应的用户身上，时间复杂度为O(n)。
	- 浪费服务器性能。当用户量非常庞大的时候，大量重复的数据会极大的影响服务器的性能。

- RBAC让不同的角色拥有不同的权限，当一个用户具有该角色的时候，对应的也就具有了该角色下的全部权限。因此，当我们想要给具有某种角色的用户增加权限的时候，我们只需要对该角色增加权限即可，将时间复杂度降低成了O(1)，而且也减轻了服务器的压力。


### 关于本项目
##### 概要
- **由简入繁，循序渐进**是本项目的主题，在这里，我要将RBAC访问控制模型的实现过程一步一步从简单到复杂的剖析展现出来。

- 在本项目中，我会补充关于**Django、python以及其他方面**的知识，因此不管是哪个版本的项目，都应该认真思考其设计的道理

##### 版本
- version1.0
	- 最简单的一个rbac



 

##### DOC

## 本项目涉及的技术
- python
- Django
- MySQL
- wsgi
- HTML
- CSS
- javascript
- jQuery



## FAQ

## changelog

## 问题交流



  



