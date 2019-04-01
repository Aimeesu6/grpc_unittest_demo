#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time : 3/22/19 3:28 PM 
# @Author : Aimee


import pymysql
from common import Const


class SQLDataBase:

    # def __init__(self,user='',password='',database='',charset=None,port=3306):
    def __init__(self, **kwargs):
        try:
            self._conn = pymysql.connect(host=kwargs["host"], user=kwargs["user"], password=kwargs["password"],
                                         charset=kwargs["charset"], database=kwargs["database"], port=kwargs["port"])
            self.__cursor = None
            print("连接数据库... ...")
        except pymysql.Error as err:
            print('数据库连接错误：' + err.msg)

    def createTable(self, tablename, **field):
        cursor = self.__getCursor()
        basesql = ""  # 定义basesql
        # 判断表名为tablename表名是否存在，如果是 直接删除
        cursor.execute("DROP TABLE IF EXISTS %s" % tablename)
        # 将field，拼接basesql
        for key in field:
            basesql = basesql + "%s varchar(255) DEFAULT NULL COMMENT '%s'," % (key, field.get(key))
        createsql = """
        CREATE TABLE %s (
            id int(11) NOT NULL AUTO_INCREMENT COMMENT '自增ID',
            %s
            PRIMARY KEY (`id`)
        )
        """ % (tablename, basesql)
        # 执行建表SQL
        cursor.execute(createsql)
        print("表:'%s' 创建成功" % tablename)

    # def findBySql(self, sql, params={}, limit=0, join='AND'):
    def findBySql(self, **kwargs):
        """
        自定义sql语句查找
        limit = 是否需要返回多少行
        params = dict(field=value)
        join = 'AND | OR'
        """
        cursor = self.__getCursor()
        # sql = self.__joinWhere(kwargs["sql"], kwargs["params"], kwargs["join"])
        if kwargs.get("join", 0) == 0:
            kwargs["join"] = "AND"
        sql = self.__joinWhere(**kwargs)
        cursor.execute(sql, tuple(kwargs["params"].values()))
        if kwargs["limit"] > 0:
            result = cursor.fetchmany(size=kwargs["limit"])
        else:
            result = cursor.fetchall()
        print("查询语句执行成功!!! 查询结果为: ")
        for r in result:
            print(r)
        return cursor.rowcount

    # def countBySql(self,sql,params = {},join = 'AND'):
    def countBySql(self, **kwargs):
        """自定义sql 统计影响行数"""
        if kwargs.get("join", 0) == 0: kwargs["join"] = "AND"
        cursor = self.__getCursor()
        # sql = self.__joinWhere(kwargs["sql"], kwargs["params"], kwargs["join"])
        sql = self.__joinWhere(**kwargs)
        cursor.execute(sql, tuple(kwargs["params"].values()))
        result = cursor.fetchall()  # fetchone是一条记录， fetchall 所有记录
        return cursor.rowcount if result else 0

    # def insert(self,table,data):
    def insert(self, **kwargs):
        """新增一条记录
          table: 表名
          data: dict 插入的数据
        """
        fields = ','.join('`' + k + '`' for k in kwargs["data"].keys())
        values = ','.join(("%s",) * len(kwargs["data"]))
        sql = 'INSERT INTO `%s` (%s) VALUES (%s)' % (kwargs["table"], fields, values)
        cursor = self.__getCursor()
        cursor.execute(sql, tuple(kwargs["data"].values()))
        # 获取插入记录的主键id
        insert_id = cursor.lastrowid
        self._conn.commit()
        return insert_id

    # def updateByAttr(self,table,data,params={},join='AND'):
    def updateByAttr(self, **kwargs):
        # 更新数据
        if kwargs.get("params", 0) == 0:
            kwargs["params"] = {}
        if kwargs.get("join", 0) == 0:
            kwargs["join"] = "AND"
        fields = ','.join('`' + k + '`=%s' for k in kwargs["data"].keys())
        values = list(kwargs["data"].values())

        values.extend(list(kwargs["params"].values()))
        sql = "UPDATE `%s` SET %s " % (kwargs["table"], fields)
        kwargs["sql"] = sql
        sql = self.__joinWhere(**kwargs)
        cursor = self.__getCursor()
        cursor.execute(sql, tuple(values))
        self._conn.commit()
        return cursor.rowcount

    # def updateByPk(self,table,data,id,pk='id'):
    def updateByPk(self, **kwargs):
        """根据主键更新，默认是id为主键"""
        return self.updateByAttr(**kwargs)

    # def deleteByAttr(self,table,params={},join='AND'):
    def deleteByAttr(self, **kwargs):
        """删除数据"""
        if kwargs.get("params", 0) == 0:
            kwargs["params"] = {}
        if kwargs.get("join", 0) == 0:
            kwargs["join"] = "AND"
        # fields = ','.join('`'+k+'`=%s' for k in kwargs["params"].keys())
        sql = "DELETE FROM `%s` " % kwargs["table"]
        kwargs["sql"] = sql
        # sql = self.__joinWhere(sql, kwargs["params"], kwargs["join"])
        sql = self.__joinWhere(**kwargs)
        cursor = self.__getCursor()
        cursor.execute(sql, tuple(kwargs["params"].values()))
        self._conn.commit()
        return cursor.rowcount

    # def deleteByPk(self,table,id,pk='id'):
    def deleteByPk(self, **kwargs):
        """根据主键删除，默认是id为主键"""
        return self.deleteByAttr(**kwargs)

    # def findByAttr(self,table,criteria = {}):
    def findByAttr(self, **kwargs):
        """根據條件查找一條記錄"""
        return self.__query(**kwargs)

    # def findByPk(self,table,id,pk='id'):
    def findByPk(self, **kwargs):
        return self.findByAttr(**kwargs)

    # def findAllByAttr(self,table,criteria={}, whole=true):
    def findAllByAttr(self, **kwargs):
        """根據條件查找記錄"""
        return self.__query(**kwargs)

    # def count(self,table,params={},join='AND'):
    def count(self, **kwargs):
        """根据条件统计行数"""
        if kwargs.get("join", 0) == 0: kwargs["join"] = "AND"
        sql = 'SELECT COUNT(*) FROM `%s`' % kwargs["table"]
        # sql = self.__joinWhere(sql, kwargs["params"], kwargs["join"])
        kwargs["sql"] = sql
        sql = self.__joinWhere(**kwargs)
        cursor = self.__getCursor()
        cursor.execute(sql, tuple(kwargs["params"].values()))
        result = cursor.fetchone()
        return result[0] if result else 0

    # def exist(self,table,params={},join='AND'):
    def exist(self, **kwargs):
        """判断是否存在"""
        return self.count(**kwargs) > 0

    def close(self):
        """关闭游标和数据库连接"""
        if self.__cursor is not None:
            self.__cursor.close()
        self._conn.close()

    def __getCursor(self):
        """获取游标"""
        if self.__cursor is None:
            self.__cursor = self._conn.cursor()
        return self.__cursor

    # def __joinWhere(self,sql,params,join):
    def __joinWhere(self, **kwargs):
        """转换params为where连接语句"""
        if kwargs["params"]:
            keys, _keys = self.__tParams(**kwargs)
            where = ' AND '.join(k + '=' + _k for k, _k in zip(keys, _keys)) if kwargs[
                                                                                    "join"] == 'AND' else ' OR '.join(
                k + '=' + _k for k, _k in zip(keys, _keys))
            kwargs["sql"] += ' WHERE ' + where
        return kwargs["sql"]

    # def __tParams(self,params):
    def __tParams(self, **kwargs):
        keys = ['`' + k + '`' for k in kwargs["params"].keys()]
        _keys = ['%s' for k in kwargs["params"].keys()]
        return keys, _keys

    # def __query(self,table,criteria,whole=False):
    def __query(self, **kwargs):
        if kwargs.get("whole", False) == False or kwargs["whole"] is not True:
            kwargs["whole"] = False
            kwargs["criteria"]['limit'] = 1
        # sql = self.__contact_sql(kwargs["table"], kwargs["criteria"])
        sql = self.__contact_sql(**kwargs)
        cursor = self.__getCursor()
        cursor.execute(sql)
        rows = cursor.fetchall() if kwargs["whole"] else cursor.fetchone()
        result = [row for row in rows] if kwargs["whole"] else rows if rows else None
        return result

    # def __contact_sql(self,table,criteria):
    def __contact_sql(self, **kwargs):
        sql = 'SELECT '
        if kwargs["criteria"] and type(kwargs["criteria"]) is dict:
            # select fields
            if 'select' in kwargs["criteria"]:
                fields = kwargs["criteria"]['select'].split(',')
                sql += ','.join('`' + field + '`' for field in fields)
            else:
                sql += ' * '
            # table
            sql += ' FROM `%s`' % kwargs["table"]
            # where
            if 'where' in kwargs["criteria"]:
                sql += ' WHERE ' + kwargs["criteria"]['where']
            # group by
            if 'group' in kwargs["criteria"]:
                sql += ' GROUP BY ' + kwargs["criteria"]['group']
            # having
            if 'having' in kwargs["criteria"]:
                sql += ' HAVING ' + kwargs["criteria"]['having']
            # order by
            if 'order' in kwargs["criteria"]:
                sql += ' ORDER BY ' + kwargs["criteria"]['order']
            # limit
            if 'limit' in kwargs["criteria"]:
                sql += ' LIMIT ' + str(kwargs["criteria"]['limit'])
            # offset
            if 'offset' in kwargs["criteria"]:
                sql += ' OFFSET ' + str(kwargs["criteria"]['offset'])
        else:
            sql += ' * FROM `%s`' % kwargs["table"]
        return sql

    def findKeySql(self, key, **kwargs):
        sqlOperate = {
            Const.COUNT: lambda: self.count(**kwargs),
            Const.COUNT_BY_SQL: lambda: self.countBySql(**kwargs),
            Const.DELETE_BY_ATTR: lambda: self.deleteByAttr(**kwargs),
            Const.EXIST: lambda: self.exist(**kwargs),
            Const.FIND_ALL_BY_ATTR: lambda: self.findAllByAttr(**kwargs),
            Const.INSERT: lambda: self.insert(**kwargs),
            Const.FIND_BY_ATTR: lambda: self.findByAttr(**kwargs),
            Const.UPDATE_BY_ATTR: lambda: self.updateByAttr(**kwargs),
            Const.FIND_BY_SQL: lambda: self.findBySql(**kwargs)
        }
        return sqlOperate[key]()


# if __name__ == "__main__":
#     sqlDB = SQLDataBase(host="127.0.0.1", user="root", password="root", charset="utf8", database="icare", port=4000)
    # 建表
    # sqlDB.createTable("senior", name="姓名", age="年龄", address="家庭住址", phone="联系电话")
    # # 根据字段统计count, join>>AND,OR,可以不传，默认为AND
    # print(sqlDB.findKeySql(Const.COUNT, table="senior", params={"name": "小包子"}))
    # # 自定义sql语句统计count
    # print(sqlDB.findKeySql(Const.COUNT_BY_SQL, sql="select * from senior", params={"name": "机构老人"}))
    # #插入数据
    # print(sqlDB.findKeySql(Const.INSERT, table="senior", data={"Name": "机构老人", "Age": "88", "Phone": "17388888888"}))
    # print(sqlDB.findKeySql(Const.INSERT, table="senior", data={"Name": "居家老人", "Age": "66", "Phone": "17366999966"}))
    # print(sqlDB.findKeySql(Const.INSERT, table="senior", data={"Name": "日托老人", "Age": "99", "Phone": "17366669999"}))
    # #根据字段删除,不传params参数，就是删除全部
    # print(sqlDB.findKeySql(Const.DELETE_BY_ATTR, table="senior", params={"Age": "66", "Name": "机构老人"}, join="OR"))
    # # 查找是否存在该记录,不传params参数，就是查找全部.join同上
    # print(sqlDB.findKeySql(Const.EXIST, table="senior", params={"id": 6, "Age": "99"}, join='OR'))
    # #根据字段查找多条记录，whole不传就查一条记录，criteria里面可以传where,group by,having,order by,limt,offset
    # print(sqlDB.findKeySql(Const.FIND_ALL_BY_ATTR, table="senior", criteria={"where": "Phone LIKE '17366%'"}, whole=True))
    # # 根据字段查一条记录，和上面的查多条记录参数基本一样，少了个whole参数
    # print(sqlDB.findKeySql(Const.FIND_BY_ATTR, table="senior", criteria={"where": "Phone LIKE '17366%'"}))
    # # 根据字段更新数据库中的记录，join可以传AND,OR,不传默认取AND
    # print(sqlDB.findKeySql(Const.UPDATE_BY_ATTR, table="senior", data={"Name": "机构A", "Age": "68"}, params={"ID": 2, "name": "机构老人"}, join='AND'))
    # 根据自定义sql语句查询记录，limit:0表示所有记录，join：AND|OR.不传取AND
    # print(sqlDB.findKeySql(Const.FIND_BY_SQL, sql="select * from senior", params={"age": "66", "Phone": '17388888888'}, limit=0, join='OR'))
