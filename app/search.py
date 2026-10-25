"""Búsqueda difusa en español (acentos, mayúsculas y errores leves)."""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-zA-Z0-9\s]", " ", texto).lower()
    return re.sub(r"\s+", " ", texto).strip()


def _puntuar(consulta: str, campos: list[str]) -> float:
    q = normalizar(consulta)
    if not q:
        return 0
    texto = normalizar(" ".join(c for c in campos if c))
    if not texto:
        return 0

    if q in texto:
        # Coincidencia directa: prioriza el inicio de una palabra.
        return 100 + (8 if f" {q}" in f" {texto}" else 0)

    tokens_q = [t for t in q.split() if len(t) > 1]
    tokens_t = texto.split()
    puntos = 0.0
    for token in tokens_q:
        if token in tokens_t:
            puntos += 34
            continue
        mejor = 0.0
        prefijo = token[: max(4, len(token) - 2)]
        for palabra in tokens_t:
            if len(token) >= 4 and palabra.startswith(prefijo):
                puntos += 30
                break
            if len(token) >= 3 and token in palabra:
                puntos += 12
            ratio = SequenceMatcher(None, token, palabra).ratio()
            if ratio > mejor:
                mejor = ratio
        if mejor >= 0.78:
            puntos += 22 * mejor
    ratio_global = SequenceMatcher(None, q, texto).ratio()
    return puntos + ratio_global * 12


def filtrar(items, consulta: str, campos, umbral: float = 18.0):
    consulta = (consulta or "").strip()
    if not consulta:
        return list(items)
    puntuados = []
    for item in items:
        if callable(campos):
            valores = campos(item)
        else:
            valores = [getattr(item, campo, "") for campo in campos]
        if isinstance(valores, str):
            valores = [valores]
        score = _puntuar(consulta, list(valores))
        if score >= umbral:
            puntuados.append((score, item))
    puntuados.sort(key=lambda par: (-par[0], getattr(par[1], "nombre", getattr(par[1], "titulo", ""))))
    return [item for _, item in puntuados]
