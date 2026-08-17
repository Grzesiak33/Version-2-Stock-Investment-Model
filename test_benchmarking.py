import pytest
from src.benchmarking import percentage_return,max_drawdown,compare_return,win_rate,ranking_effectiveness
def test_return(): assert percentage_return(100,110)==pytest.approx(.1)
def test_relative(): assert compare_return(.1,.06)==pytest.approx(.04)
def test_drawdown(): assert max_drawdown([100,120,90,110])==pytest.approx(-.25)
def test_win_rate(): assert win_rate([.1,-.1,.2])==pytest.approx(2/3)
def test_ranking_effectiveness(): assert ranking_effectiveness([3,2,1],[.3,.2,.1])==pytest.approx(1)
