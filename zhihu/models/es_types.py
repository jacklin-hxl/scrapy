
from datetime import datetime

from elasticsearch_dsl import DocType, Date, Integer, Keyword, Text, Completion
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer


connections.create_connection("default")

class customAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer =customAnalyzer('ik_max_word',filter=['lowercase'])

class ZhihuQuestionType(DocType):
    suggest =Completion(analyzer=ik_analyzer)
    question_id = Keyword()
    topics = Text(analyzer="ik_max_word")
    url = Keyword()
    title = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    comments_num = Integer()
    answer_num = Integer()
    attention_num = Integer()
    click_num = Integer()
    crawl_time = Date()

    class Meta:
        index = "zhihu"
        doc_type = "zhihu_question"

class ZhihuAnswerType(DocType):
    suggest =Completion(analyzer=ik_analyzer)
    answer_id = Keyword()
    url = Keyword()
    question_id = Keyword()
    author_id = Keyword()
    content = Text(analyzer="ik_max_word")
    praise_num = Integer()
    comments_num = Integer()
    create_time = Date()
    update_time = Date()
    crawl_time = Date()

    class Meta:
        index = "zhihu"
        doc_type = "zhihu_answer"


if __name__ == "__main__":
    ZhihuAnswerType.init()
    ZhihuQuestionType.init()