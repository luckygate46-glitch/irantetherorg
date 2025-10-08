import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Button } from '@/components/ui/button.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Puzzle, Trophy, RefreshCw, Home, Clock, Star } from 'lucide-react';

const KYCWaitingGame = ({ user }) => {
  const navigate = useNavigate();
  const [gameType, setGameType] = useState('puzzle');
  const [score, setScore] = useState(0);
  const [level, setLevel] = useState(1);
  const [timeLeft, setTimeLeft] = useState(60);
  const [gameActive, setGameActive] = useState(false);
  const [puzzleGrid, setPuzzleGrid] = useState([]);
  const [targetPattern, setTargetPattern] = useState([]);

  // Initialize crypto-themed puzzle
  const cryptoSymbols = ['₿', 'Ξ', '₳', '◊', '⊕', '●', '◆', '★'];
  
  useEffect(() => {
    initializePuzzle();
  }, [level]);

  useEffect(() => {
    let timer;
    if (gameActive && timeLeft > 0) {
      timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
    } else if (timeLeft === 0) {
      endGame();
    }
    return () => clearTimeout(timer);
  }, [gameActive, timeLeft]);

  const initializePuzzle = () => {
    const gridSize = Math.min(3 + level, 6);
    const newGrid = Array(gridSize).fill().map(() => 
      Array(gridSize).fill().map(() => 
        cryptoSymbols[Math.floor(Math.random() * cryptoSymbols.length)]
      )
    );
    
    const newTarget = Array(gridSize).fill().map(() => 
      Array(gridSize).fill().map(() => 
        cryptoSymbols[Math.floor(Math.random() * cryptoSymbols.length)]
      )
    );
    
    setPuzzleGrid(newGrid);
    setTargetPattern(newTarget);
  };

  const startGame = () => {
    setGameActive(true);
    setTimeLeft(60 + (level * 10));
    setScore(0);
    initializePuzzle();
  };

  const endGame = () => {
    setGameActive(false);
    if (score >= level * 100) {
      setLevel(level + 1);
    }
  };

  const handleCellClick = (row, col) => {
    if (!gameActive) return;
    
    const newGrid = [...puzzleGrid];
    const currentIndex = cryptoSymbols.indexOf(newGrid[row][col]);
    newGrid[row][col] = cryptoSymbols[(currentIndex + 1) % cryptoSymbols.length];
    setPuzzleGrid(newGrid);
    
    // Check if matches target
    if (newGrid[row][col] === targetPattern[row][col]) {
      setScore(score + 10);
    }
  };

  const resetGame = () => {
    setGameActive(false);
    setScore(0);
    setLevel(1);
    setTimeLeft(60);
    initializePuzzle();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-4" dir="rtl">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <Card className="mb-6">
          <CardHeader className="text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Puzzle className="w-8 h-8 text-purple-500" />
              <CardTitle className="text-2xl text-white">بازی انتظار تایید KYC</CardTitle>
            </div>
            <p className="text-gray-400">در انتظار تایید مدارک، با بازی‌های کریپتو وقت خود را پر کنید!</p>
          </CardHeader>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Game Stats */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Trophy className="w-5 h-5 text-yellow-500" />
                آمار بازی
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">امتیاز:</span>
                <Badge variant="secondary" className="text-lg px-3 py-1">
                  {score}
                </Badge>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-400">سطح:</span>
                <Badge variant="outline" className="text-lg px-3 py-1">
                  {level}
                </Badge>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-400">زمان باقی‌مانده:</span>
                <Badge variant={timeLeft < 10 ? "destructive" : "default"} className="text-lg px-3 py-1">
                  <Clock className="w-4 h-4 mr-1" />
                  {timeLeft}s
                </Badge>
              </div>

              <div className="pt-4 space-y-2">
                {!gameActive ? (
                  <Button 
                    onClick={startGame} 
                    className="w-full bg-green-600 hover:bg-green-700"
                  >
                    شروع بازی
                  </Button>
                ) : (
                  <Button 
                    onClick={endGame} 
                    variant="outline" 
                    className="w-full"
                  >
                    پایان بازی
                  </Button>
                )}
                
                <Button 
                  onClick={resetGame} 
                  variant="outline" 
                  className="w-full"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  شروع مجدد
                </Button>
                
                <Button 
                  onClick={() => navigate('/dashboard')} 
                  variant="ghost" 
                  className="w-full"
                >
                  <Home className="w-4 h-4 mr-2" />
                  بازگشت به داشبورد
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Main Game Area */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-lg text-white text-center">
                کریپتو پازل - سطح {level}
              </CardTitle>
              <p className="text-gray-400 text-center text-sm">
                روی خانه‌ها کلیک کنید تا با الگوی هدف مطابقت دهید
              </p>
            </CardHeader>
            <CardContent>
              {/* Target Pattern */}
              <div className="mb-6">
                <h3 className="text-white text-center mb-3 flex items-center justify-center gap-2">
                  <Star className="w-4 h-4 text-yellow-500" />
                  الگوی هدف
                </h3>
                <div className="grid gap-1 justify-center" style={{
                  gridTemplateColumns: `repeat(${targetPattern.length}, minmax(0, 1fr))`
                }}>
                  {targetPattern.map((row, rowIndex) => 
                    row.map((cell, colIndex) => (
                      <div
                        key={`target-${rowIndex}-${colIndex}`}
                        className="w-12 h-12 bg-yellow-900/30 border border-yellow-600 flex items-center justify-center text-2xl text-yellow-400 font-bold rounded"
                      >
                        {cell}
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Game Grid */}
              <div>
                <h3 className="text-white text-center mb-3">پازل شما</h3>
                <div className="grid gap-1 justify-center" style={{
                  gridTemplateColumns: `repeat(${puzzleGrid.length}, minmax(0, 1fr))`
                }}>
                  {puzzleGrid.map((row, rowIndex) => 
                    row.map((cell, colIndex) => (
                      <button
                        key={`game-${rowIndex}-${colIndex}`}
                        onClick={() => handleCellClick(rowIndex, colIndex)}
                        disabled={!gameActive}
                        className={`
                          w-12 h-12 border-2 flex items-center justify-center text-2xl font-bold rounded transition-all
                          ${gameActive ? 'hover:scale-105 cursor-pointer' : 'cursor-not-allowed opacity-50'}
                          ${cell === targetPattern[rowIndex][colIndex] 
                            ? 'bg-green-600/50 border-green-400 text-green-200' 
                            : 'bg-slate-700 border-slate-500 text-white hover:bg-slate-600'
                          }
                        `}
                      >
                        {cell}
                      </button>
                    ))
                  )}
                </div>
              </div>

              {/* Game Instructions */}
              <div className="mt-6 p-4 bg-slate-800 rounded-lg">
                <h4 className="text-white font-semibold mb-2">راهنما:</h4>
                <ul className="text-gray-400 text-sm space-y-1">
                  <li>• روی هر خانه کلیک کنید تا نماد آن تغییر کند</li>
                  <li>• سعی کنید الگوی خود را با الگوی هدف مطابقت دهید</li>
                  <li>• خانه‌های درست رنگ سبز می‌شوند</li>
                  <li>• با هر سطح، پازل پیچیده‌تر می‌شود</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* KYC Status Reminder */}
        <Card className="mt-6">
          <CardContent className="text-center py-6">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Clock className="w-5 h-5 text-orange-500" />
              <span className="text-white font-semibold">وضعیت KYC</span>
            </div>
            <p className="text-gray-400 mb-4">
              مدارک شما در حال بررسی است. پس از تایید، به تمام امکانات دسترسی خواهید داشت.
            </p>
            <Button 
              onClick={() => navigate('/kyc')} 
              variant="outline"
              className="mr-3"
            >
              مشاهده وضعیت KYC
            </Button>
            <Button 
              onClick={() => navigate('/dashboard')}
              className="bg-blue-600 hover:bg-blue-700"
            >
              داشبورد اصلی
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default KYCWaitingGame;