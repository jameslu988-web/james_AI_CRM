"""向量知识库API路由"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import traceback
import json

from src.crm.database import get_session, KnowledgeDocument, KnowledgeChunk
from src.ai.vector_knowledge import VectorKnowledgeService

router = APIRouter()


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


class SearchRequest(BaseModel):
    """向量搜索请求"""
    query: str
    limit: int = 5
    category: Optional[str] = None


class SearchResult(BaseModel):
    """搜索结果"""
    id: int
    document_id: int
    content: str
    similarity: float
    metadata: Dict
    document_title: str


@router.post("/knowledge/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("general"),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    上传文档到知识库
    
    支持格式：PDF、Word、TXT
    """
    try:
        # 验证文件格式
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_ext = '.' + file.filename.split('.')[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件格式。支持格式: {', '.join(allowed_extensions)}"
            )
        
        # 读取文件内容
        file_content = await file.read()
        
        # 初始化向量服务
        vector_service = VectorKnowledgeService()
        
        # 处理并上传文档
        result = await vector_service.upload_document(
            file_content=file_content,
            filename=file.filename,
            title=title,
            category=category,
            description=description,
            db_session=db
        )
        
        return {
            "success": True,
            "message": "文档上传成功",
            "document": result
        }
        
    except Exception as e:
        print(f"❌ 文档上传失败: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/knowledge/search", response_model=List[SearchResult])
async def search_knowledge(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    向量搜索知识库
    
    使用语义搜索查找相关文档片段
    """
    try:
        vector_service = VectorKnowledgeService()
        
        results = await vector_service.search_similar(
            query=request.query,
            limit=request.limit,
            category=request.category,
            db_session=db
        )
        
        # 格式化返回结果
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result["id"],
                "document_id": result["document_id"],
                "content": result["content"],
                "similarity": result["similarity"],
                "metadata": result["metadata"],
                "document_title": result["document_title"]
            })
        
        return formatted_results
        
    except Exception as e:
        print(f"❌ 知识库搜索失败: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/knowledge/documents")
async def list_documents(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """获取文档列表"""
    try:
        query = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.is_active == True
        )
        
        if category:
            query = query.filter(KnowledgeDocument.category == category)
        
        total = query.count()
        documents = query.order_by(
            KnowledgeDocument.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "data": [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "filename": doc.filename,
                    "category": doc.category,
                    "summary": doc.summary,
                    "file_size": doc.file_size,
                    "chunk_count": doc.chunk_count,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None
                }
                for doc in documents
            ]
        }
        
    except Exception as e:
        print(f"❌ 获取文档列表失败: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取列表失败: {str(e)}")


@router.get("/knowledge/documents/{document_id}")
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """获取文档详情（包括完整内容）"""
    try:
        document = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.id == document_id,
            KnowledgeDocument.is_active == True
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 获取所有分块内容，按顺序拼接
        chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.document_id == document_id
        ).order_by(KnowledgeChunk.chunk_index).all()
        
        # 拼接完整内容
        full_content = "\n".join([chunk.content for chunk in chunks])
        
        return {
            "id": document.id,
            "title": document.title,
            "filename": document.filename,
            "category": document.category,
            "summary": document.summary,
            "content": full_content,  # 完整内容
            "file_size": document.file_size,
            "chunk_count": document.chunk_count,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "updated_at": document.updated_at.isoformat() if document.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 获取文档详情失败: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.put("/knowledge/documents/{document_id}")
async def update_document(
    document_id: int,
    title: str = Form(...),
    category: str = Form("general"),
    summary: Optional[str] = Form(None),
    content: Optional[str] = Form(None),  # 新增：支持内容编辑
    db: Session = Depends(get_db)
):
    """更新文档信息，如果提供了content则重新生成向量"""
    try:
        document = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.id == document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 更新基本信息
        document.title = title
        document.category = category
        if summary is not None:
            document.summary = summary
        document.updated_at = datetime.now()
        
        # 如果提供了新内容，重新生成向量
        if content is not None and content.strip():
            print(f"📝 内容已修改，重新生成向量...")
            
            # 更新文档内容
            document.content = content[:5000]  # 保存前5000字符作为预览
            document.status = 'processing'
            db.commit()
            
            # 删除旧的分块
            db.query(KnowledgeChunk).filter(
                KnowledgeChunk.document_id == document_id
            ).delete()
            db.commit()
            
            # 重新分块
            vector_service = VectorKnowledgeService()
            chunks = vector_service.split_text(content)
            print(f"✂️ 生成 {len(chunks)} 个新分块")
            
            # 向量化所有分块
            print(f"🧪 向量化文本...")
            embeddings = await vector_service.batch_create_embeddings(chunks)
            
            # 保存新分块
            print(f"💾 保存到数据库...")
            for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk = KnowledgeChunk(
                    document_id=document.id,
                    content=chunk_text,
                    chunk_index=idx,
                    embedding=json.dumps(embedding),
                    chunk_metadata=json.dumps({}),
                    token_count=len(chunk_text.split()),
                    char_count=len(chunk_text)
                )
                db.add(chunk)
            
            document.chunk_count = len(chunks)
            document.status = 'completed'
            print(f"✅ 向量重新生成完成")
        
        db.commit()
        db.refresh(document)
        
        return {
            "success": True,
            "message": "文档信息已更新" if content is None else "文档内容已更新并重新生成向量",
            "document": {
                "id": document.id,
                "title": document.title,
                "category": document.category,
                "summary": document.summary,
                "chunk_count": document.chunk_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 更新文档失败: {str(e)}")
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete("/knowledge/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """删除文档"""
    try:
        document = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.id == document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 软删除
        document.is_active = False
        db.commit()
        
        return {
            "success": True,
            "message": "文档已删除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 删除文档失败: {str(e)}")
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/knowledge/categories")
async def get_categories(db: Session = Depends(get_db)):
    """获取所有知识库分类"""
    try:
        categories = db.query(KnowledgeDocument.category).distinct().all()
        
        return {
            "categories": [cat[0] for cat in categories if cat[0]]
        }
        
    except Exception as e:
        print(f"❌ 获取分类失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取分类失败: {str(e)}")
