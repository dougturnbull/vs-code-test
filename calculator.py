from __future__ import annotations

import ast
import math
import operator
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Calculator")


class CalcRequest(BaseModel):
	expression: str = Field(..., min_length=1, max_length=200)


class CalcResponse(BaseModel):
	result: float


_BIN_OPS: dict[type[ast.operator], Any] = {
	ast.Add: operator.add,
	ast.Sub: operator.sub,
	ast.Mult: operator.mul,
	ast.Div: operator.truediv,
	ast.Pow: operator.pow,
}

_UNARY_OPS: dict[type[ast.unaryop], Any] = {
	ast.UAdd: operator.pos,
	ast.USub: operator.neg,
}


def _eval_node(node: ast.AST) -> float:
	if isinstance(node, ast.Expression):
		return _eval_node(node.body)

	if isinstance(node, ast.Constant):
		if isinstance(node.value, bool):
			raise ValueError("Only numbers are allowed")
		if isinstance(node.value, (int, float)):
			return float(node.value)
		raise ValueError("Only numbers are allowed")

	if isinstance(node, ast.Call):
		if not isinstance(node.func, ast.Name):
			raise ValueError("Unsupported function")
		if node.func.id != "sqrt":
			raise ValueError("Unsupported function")
		if len(node.args) != 1 or node.keywords:
			raise ValueError("sqrt() takes one argument")
		value = _eval_node(node.args[0])
		if value < 0:
			raise ValueError("sqrt() domain error")
		return float(math.sqrt(value))

	if isinstance(node, ast.UnaryOp):
		op_type = type(node.op)
		if op_type not in _UNARY_OPS:
			raise ValueError("Unsupported unary operator")
		return float(_UNARY_OPS[op_type](_eval_node(node.operand)))

	if isinstance(node, ast.BinOp):
		op_type = type(node.op)
		if op_type not in _BIN_OPS:
			raise ValueError("Unsupported operator")
		left = _eval_node(node.left)
		right = _eval_node(node.right)
		if op_type is ast.Div and right == 0:
			raise ZeroDivisionError("Division by zero")
		return float(_BIN_OPS[op_type](left, right))

	raise ValueError("Unsupported expression")


def safe_eval_expression(expression: str) -> float:
	expr = expression.strip()
	if not expr:
		raise ValueError("Empty expression")
	if len(expr) > 200:
		raise ValueError("Expression too long")

	# UI convenience: support ^ for exponent and √ for square root.
	expr = expr.replace("^", "**").replace("√", "sqrt")

	try:
		tree = ast.parse(expr, mode="eval")
	except SyntaxError as exc:
		raise ValueError("Invalid expression") from exc

	return _eval_node(tree)


@app.get("/")
def index() -> FileResponse:
	index_file = STATIC_DIR / "index.html"
	if not index_file.exists():
		raise HTTPException(status_code=500, detail="Missing static/index.html")
	return FileResponse(index_file)


@app.post("/api/calc", response_model=CalcResponse)
def calc(request: CalcRequest) -> CalcResponse:
	try:
		result = safe_eval_expression(request.expression)
	except ZeroDivisionError as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc
	return CalcResponse(result=result)


if STATIC_DIR.exists():
	app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":
	import uvicorn

	uvicorn.run("calculator:app", host="127.0.0.1", port=8000, reload=True)