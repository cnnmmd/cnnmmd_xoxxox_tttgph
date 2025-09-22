from typing import TypedDict, List,  Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_allama import ChatOllama
from xoxxox.shared import Custom, PrcFlw

#---------------------------------------------------------------------------

# 調整：ログ（プロンプト向け）
class MgrLog:
  deflog = 1

  @staticmethod
  def maxlog(config) -> int:
    return (config or {}).get("configurable", {}).get("maxlog", MgrLog.deflog)

  @staticmethod
  def trmlog(config, lstmsg):
    m = MgrLog.maxlog(config)
    l = lstmsg
    if len(l) >= m + 2:
      l.pop(0)
      l.pop(0)
    return l

# 設定：ステートマシン：ステート
class SState(TypedDict):
  lstmsg: Annotated[List[BaseMessage], add_messages]

# 設定：ステートマシン：グラフ
class TttPrc:
  # 初期
  def __init__(self, config="xoxxox/config_tttgph_cmm001", **dicprm):
    diccnf = Custom.update(config, dicprm)
    self.mdlold = ""

  # 定義
  def status(self, config="xoxxox/config_tttgph_cmm001", **dicprm):
    diccnf = Custom.update(config, dicprm)
    lngcha = diccnf["lngcha"]
    nmodel = diccnf["nmodel"]
    status = diccnf["status"]
    numtmp = diccnf["numtmp"]
    maxtkn = diccnf["maxtkn"]
    self.maxlog = diccnf["maxlog"]
    self.expert = diccnf["expert"]

    # 作成：モデル
    if mdlcrr != self.mdlold:
      if lngcha == "ChatOpenAI":
        mdlcrr = ChatOpenAI(model=nmodel)
      if lngcha == "ChatOllama":
        dicsrv = PrcFlw.dicsrv()
        mdlcrr = ChatOllama(model=nmodel, base_url=dicsrv["xoxxox_appolm"])
      self.mdlold = mdlcrr
    mdlcrr = mdlcrr.bind(temperature=numtmp, max_tokens=maxtkn)

    # 定義：ノード
    def nodcha(sstate: SState, *, config) -> SState:
      lstlog = MgrLog.trmlog(config, sstate["lstmsg"])
      prompt = [SystemMessage(content=status)] + lstlog
      print("prompt[", prompt, "]") # DBG
      result = mdlcrr.invoke(prompt)
      dicsst = {"lstmsg": [AIMessage(content=result.content)]}
      return dicsst

    # 定義：グラフ（ノード＋エッジ）
    sgraph = StateGraph(SState)
    sgraph.add_node("nodcha", nodcha)
    sgraph.add_edge(START, "nodcha")
    sgraph.add_edge("nodcha", END)
    self.appgrp = sgraph.compile(checkpointer=MemorySaver())

  # 推定
  def infere(self, txtreq: str) -> str:
    dicsst = {"lstmsg": [HumanMessage(content=txtreq)]}
    result = self.appgrp.invoke(dicsst, config={"configurable": {"thread_id": self.expert, "maxlog": self.maxlog}})
    txtres = result["lstmsg"][-1].content
    txtopt = ""
    return (txtres, txtopt)
