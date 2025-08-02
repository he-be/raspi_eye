import math
from typing import Callable

class Easing:
    """イージング関数のコレクション"""
    
    @staticmethod
    def linear(t: float) -> float:
        """線形補間"""
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        """二次関数イーズイン"""
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        """二次関数イーズアウト"""
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """二次関数イーズインアウト"""
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - 2 * (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """三次関数イーズイン"""
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """三次関数イーズアウト"""
        return 1 - (1 - t) ** 3
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """三次関数イーズインアウト"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - 4 * (1 - t) ** 3
    
    @staticmethod
    def ease_in_sine(t: float) -> float:
        """サイン関数イーズイン"""
        return 1 - math.cos(t * math.pi / 2)
    
    @staticmethod
    def ease_out_sine(t: float) -> float:
        """サイン関数イーズアウト"""
        return math.sin(t * math.pi / 2)
    
    @staticmethod
    def ease_in_out_sine(t: float) -> float:
        """サイン関数イーズインアウト"""
        return -(math.cos(math.pi * t) - 1) / 2
    
    @staticmethod
    def bounce_out(t: float) -> float:
        """バウンスアウト"""
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375

def lerp(start: float, end: float, t: float, easing_func: Callable[[float], float] = None) -> float:
    """線形補間（イージング関数対応）
    
    Args:
        start: 開始値
        end: 終了値
        t: 補間係数（0.0-1.0）
        easing_func: イージング関数（省略時は線形）
        
    Returns:
        補間された値
    """
    t = max(0.0, min(1.0, t))  # クランプ
    
    if easing_func:
        t = easing_func(t)
    
    return start + (end - start) * t

def lerp_color(start_color: tuple, end_color: tuple, t: float, easing_func: Callable[[float], float] = None) -> tuple:
    """色の線形補間
    
    Args:
        start_color: 開始色 (R, G, B)
        end_color: 終了色 (R, G, B)
        t: 補間係数（0.0-1.0）
        easing_func: イージング関数
        
    Returns:
        補間された色 (R, G, B)
    """
    r = int(lerp(start_color[0], end_color[0], t, easing_func))
    g = int(lerp(start_color[1], end_color[1], t, easing_func))
    b = int(lerp(start_color[2], end_color[2], t, easing_func))
    
    return (r, g, b)