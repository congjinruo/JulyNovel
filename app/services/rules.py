#coding=utf-8
import re
from multiprocessing import Pool
import os, time, random
#print('//qidian.qpic.cn/qdbimg/349573/1010438082/180 \f\n\r\t\v'.strip())


#替换换行符...
#print(re.sub(r'\s+', '', '//qidian.qpic.cn/qdbimg/349573/1010438082/180 \f\n\r\t\vDDD'))
#分割字符
#print(re.split(r'[\：\章]', '首发时间：2017-08-28 14:11:47 章节字数：2301', 3))

#print('12345'[:-1])


"""
def long_time_task(name):
    print('Run task %s (%s)...' % (name, os.getpid()))
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print('Task %s runs %0.2f seconds.' % (name, (end - start)))

if __name__=='__main__':
    print('Parent process %s.' % os.getpid())
    p = Pool(2)
    for i in range(3):
        p.apply_async(long_time_task, args=(i,))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
"""

"""
继承connection 增加totalCount
class MyConnection(Connection):
    class Meta:
        node = UserType

    total_count = Int()

some_query = ConnectionField(MyConnection)

def resolve_some_query(self, *_):
  edges = .. create edges from query ...
  total_count = .. calculate total ...
  return MyConnection
      total_count=total_count,
      edges=edges,
      page_info=PageInfo(
            start_cursor=start_cursor.urlsafe() if start_cursor else '',
            end_cursor=end_cursor,
            has_previous_page=has_previous_page,
            has_next_page=ndb_iter.has_next()
        )
  )
"""




