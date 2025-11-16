"""
LangGraph workflow for admissions counseling chatbot
"""

from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
import logging

from app.config import settings
from app.services.search import get_search_engine
from app.services.answer_generator import get_answer_generator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define workflow state
class ChatbotState(TypedDict):
    """State for chatbot workflow"""
    # Input
    query: str
    conversation_history: Optional[List[Dict[str, str]]]
    
    # Intermediate
    retrieved_documents: List[Dict[str, Any]]
    context: str
    
    # Output
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    # Control
    should_retrieve: bool
    has_context: bool
    error: Optional[str]


class AdmissionsChatbotWorkflow:
    """
    LangGraph workflow for admissions counseling chatbot

    Workflow:
    1. Input validation
    2. Retrieval (hybrid search + reranking)
    3. Context check
    4. Answer generation
    5. Output formatting
    """

    def __init__(self, search_service=None, answer_generator=None):
        """
        Initialize workflow components

        Args:
            search_service: Pre-loaded search service (optional, will create new if None)
            answer_generator: Pre-loaded answer generator (optional, will create new if None)
        """
        # Use provided instances or create new ones
        self.search_engine = search_service if search_service else get_search_engine()
        self.answer_generator = answer_generator if answer_generator else get_answer_generator()

        # Build workflow graph
        self.workflow = self._build_workflow()
        logger.info("✅ Chatbot workflow initialized")
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow"""
        # Create graph
        workflow = StateGraph(ChatbotState)
        
        # Add nodes
        workflow.add_node("validate_input", self.validate_input)
        workflow.add_node("retrieve_context", self.retrieve_context)
        workflow.add_node("generate_answer", self.generate_answer)
        workflow.add_node("format_output", self.format_output)
        workflow.add_node("handle_no_context", self.handle_no_context)
        
        # Set entry point
        workflow.set_entry_point("validate_input")
        
        # Add edges
        workflow.add_edge("validate_input", "retrieve_context")
        
        # Conditional edge after retrieval
        workflow.add_conditional_edges(
            "retrieve_context",
            self.check_context,
            {
                "has_context": "generate_answer",
                "no_context": "handle_no_context"
            }
        )
        
        workflow.add_edge("generate_answer", "format_output")
        workflow.add_edge("handle_no_context", "format_output")
        workflow.add_edge("format_output", END)
        
        return workflow.compile()
    
    def validate_input(self, state: ChatbotState) -> ChatbotState:
        """
        Validate and preprocess input
        
        Args:
            state: Current workflow state
        
        Returns:
            Updated state
        """
        logger.info(f"📝 Validating input: {state['query'][:50]}...")
        
        # Basic validation
        query = state["query"].strip()
        
        if not query:
            state["error"] = "Empty query"
            state["should_retrieve"] = False
            return state
        
        # Update state
        state["query"] = query
        state["should_retrieve"] = True
        state["error"] = None
        
        logger.info("✅ Input validated")
        return state
    
    def retrieve_context(self, state: ChatbotState) -> ChatbotState:
        """
        Retrieve relevant context using hybrid search + reranking
        
        Args:
            state: Current workflow state
        
        Returns:
            Updated state with retrieved documents
        """
        if not state.get("should_retrieve", True):
            logger.warning("⚠️  Skipping retrieval")
            state["retrieved_documents"] = []
            state["has_context"] = False
            return state
        
        logger.info(f"🔍 Retrieving context for: {state['query'][:50]}...")
        
        try:
            # Perform hybrid search with reranking
            documents = self.search_engine.hybrid_search(
                query=state["query"],
                top_k=settings.RERANKER_TOP_N,
                use_reranker=True
            )
            
            state["retrieved_documents"] = documents
            state["has_context"] = len(documents) > 0
            
            logger.info(f"✅ Retrieved {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"❌ Retrieval error: {e}")
            state["retrieved_documents"] = []
            state["has_context"] = False
            state["error"] = f"Retrieval error: {str(e)}"
        
        return state
    
    def check_context(self, state: ChatbotState) -> str:
        """
        Check if sufficient context was retrieved
        
        Args:
            state: Current workflow state
        
        Returns:
            Next node name
        """
        if state.get("has_context", False):
            return "has_context"
        else:
            return "no_context"
    
    def generate_answer(self, state: ChatbotState) -> ChatbotState:
        """
        Generate answer using LLM
        
        Args:
            state: Current workflow state
        
        Returns:
            Updated state with generated answer
        """
        logger.info("🤖 Generating answer...")
        
        try:
            # Generate answer
            result = self.answer_generator.generate_answer(
                query=state["query"],
                retrieved_contexts=state["retrieved_documents"],
                conversation_history=state.get("conversation_history"),
                conversation_id=state.get("conversation_id")
            )
            
            state["answer"] = result["answer"]
            state["metadata"] = {
                "generation_model": result["model"],
                "tokens_used": result["tokens_used"],
                "generation_successful": result["generation_successful"],
                "fallback_used": result["fallback_used"]
            }
            
            logger.info(f"✅ Answer generated: {result['answer'][:100]}...")
            
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            state["answer"] = "Xin lỗi, tôi gặp lỗi khi tạo câu trả lời. Vui lòng thử lại."
            state["error"] = f"Generation error: {str(e)}"
            state["metadata"] = {
                "generation_successful": False,
                "error": str(e)
            }
        
        return state
    
    def handle_no_context(self, state: ChatbotState) -> ChatbotState:
        """
        Handle case when no relevant context is found
        
        Args:
            state: Current workflow state
        
        Returns:
            Updated state with fallback answer
        """
        logger.warning("⚠️  No context found, using fallback")
        
        state["answer"] = """Xin lỗi, tôi không tìm thấy thông tin liên quan đến câu hỏi của bạn trong cơ sở dữ liệu tuyển sinh.

Bạn có thể:
- Thử diễn đạt câu hỏi theo cách khác
- Cung cấp thêm chi tiết cụ thể
- Liên hệ trực tiếp với phòng tuyển sinh để được hỗ trợ

Tôi có thể giúp bạn với các câu hỏi về:
- Điều kiện xét tuyển
- Phương thức xét tuyển
- Hồ sơ đăng ký
- Học phí và học bổng
- Thời gian tuyển sinh"""
        
        state["metadata"] = {
            "generation_successful": False,
            "fallback_used": True,
            "reason": "no_context_found"
        }
        
        return state
    
    def format_output(self, state: ChatbotState) -> ChatbotState:
        """
        Format final output
        
        Args:
            state: Current workflow state
        
        Returns:
            Updated state with formatted output
        """
        logger.info("📦 Formatting output...")
        
        # Prepare sources
        sources = []
        for doc in state.get("retrieved_documents", [])[:3]:  # Top 3 sources
            source = {
                "question": doc.get("question", ""),
                "article": doc.get("article", ""),
                "document": doc.get("document", ""),
                "score": doc.get("score", 0.0)
            }
            if "reranker_score" in doc:
                source["reranker_score"] = doc["reranker_score"]
            sources.append(source)
        
        state["sources"] = sources
        
        # Add retrieval metadata
        if "metadata" not in state:
            state["metadata"] = {}
        
        state["metadata"].update({
            "num_documents_retrieved": len(state.get("retrieved_documents", [])),
            "retrieval_method": "hybrid_search_with_reranking",
            "reranker_enabled": settings.RERANKER_ENABLED,
            "workflow": "langgraph"
        })
        
        logger.info("✅ Output formatted")
        return state
    
    def run(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Run the chatbot workflow
        
        Args:
            query: User's question
            conversation_history: Optional conversation history
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
        logger.info(f"🚀 Running workflow for query: {query[:50]}...")
        
        # Initialize state
        initial_state = ChatbotState(
            query=query,
            conversation_history=conversation_history,
            retrieved_documents=[],
            context="",
            answer="",
            sources=[],
            metadata={},
            should_retrieve=True,
            has_context=False,
            error=None
        )
        
        try:
            # Run workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Return result
            return {
                "query": final_state["query"],
                "answer": final_state["answer"],
                "sources": final_state["sources"],
                "metadata": final_state["metadata"]
            }
        
        except Exception as e:
            logger.error(f"❌ Workflow error: {e}")
            return {
                "query": query,
                "answer": "Xin lỗi, hệ thống gặp lỗi. Vui lòng thử lại sau.",
                "sources": [],
                "metadata": {
                    "error": str(e),
                    "workflow": "langgraph",
                    "generation_successful": False
                }
            }


# Global workflow instance
_workflow_instance = None


def get_chatbot_workflow() -> AdmissionsChatbotWorkflow:
    """Get or create global workflow instance"""
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = AdmissionsChatbotWorkflow()
    return _workflow_instance

