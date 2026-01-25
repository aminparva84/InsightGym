import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './PsychologyTest.css';

const PsychologyTest = () => {
  const { t, i18n } = useTranslation();
  const [activeTest, setActiveTest] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [results, setResults] = useState({});

  // Exercise Personality Assessment Questions (15 questions)
  const exercisePersonalityQuestions = i18n.language === 'fa' ? [
    { id: 1, question: 'من ترجیح می‌دهم به تنهایی تمرین کنم تا در گروه', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 2, question: 'من از چالش‌های فیزیکی لذت می‌برم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 3, question: 'من نیاز به برنامه منظم برای تمرینات دارم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 4, question: 'من از رقابت با دیگران انگیزه می‌گیرم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 5, question: 'من ترجیح می‌دهم تمرینات متنوع انجام دهم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 6, question: 'من از تمرینات شدید و چالش‌برانگیز لذت می‌برم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 7, question: 'من نیاز به بازخورد فوری از پیشرفت خود دارم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 8, question: 'من از تمرینات تکراری خسته می‌شوم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 9, question: 'من ترجیح می‌دهم در محیط آرام تمرین کنم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 10, question: 'من از هدف‌گذاری و دستیابی به اهداف لذت می‌برم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 11, question: 'من نیاز به انعطاف‌پذیری در برنامه تمرینی دارم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 12, question: 'من از یادگیری تکنیک‌های جدید هیجان‌زده می‌شوم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 13, question: 'من ترجیح می‌دهم تمرینات کوتاه و شدید انجام دهم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 14, question: 'من از تمرینات گروهی و اجتماعی لذت می‌برم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 15, question: 'من نیاز به ساختار و نظم در تمرینات دارم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] }
  ] : [
    { id: 1, question: 'I prefer to exercise alone rather than in a group', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 2, question: 'I enjoy physical challenges', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 3, question: 'I need a regular schedule for workouts', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 4, question: 'I get motivated by competing with others', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 5, question: 'I prefer to do varied exercises', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 6, question: 'I enjoy intense and challenging workouts', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 7, question: 'I need immediate feedback on my progress', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 8, question: 'I get bored with repetitive exercises', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 9, question: 'I prefer to exercise in a quiet environment', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 10, question: 'I enjoy setting goals and achieving them', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 11, question: 'I need flexibility in my workout schedule', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 12, question: 'I get excited about learning new techniques', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 13, question: 'I prefer short and intense workouts', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 14, question: 'I enjoy group and social exercises', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 15, question: 'I need structure and order in my workouts', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] }
  ];

  // Emotional Intelligence (EQ) Test in Sports Questions (12 questions)
  const eqTestQuestions = i18n.language === 'fa' ? [
    { id: 1, question: 'من می‌توانم احساسات خود را در حین تمرین کنترل کنم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 2, question: 'من می‌توانم احساسات دیگران را در محیط ورزشی درک کنم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 3, question: 'من در مواجهه با شکست انگیزه خود را حفظ می‌کنم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 4, question: 'من می‌توانم استرس را در حین تمرین مدیریت کنم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 5, question: 'من از بازخورد سازنده استقبال می‌کنم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 6, question: 'من می‌توانم با تیم همکاری موثری داشته باشم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 7, question: 'من می‌توانم انگیزه خود را در طول زمان حفظ کنم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 8, question: 'من می‌توانم احساسات منفی را به انرژی مثبت تبدیل کنم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 9, question: 'من درک خوبی از نقاط قوت و ضعف خود دارم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 10, question: 'من می‌توانم در شرایط دشوار آرامش خود را حفظ کنم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 11, question: 'من می‌توانم با مربی و هم‌تیمی‌ها ارتباط موثری برقرار کنم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 12, question: 'من از اشتباهات خود درس می‌گیرم و پیشرفت می‌کنم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] }
  ] : [
    { id: 1, question: 'I can control my emotions during exercise', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 2, question: 'I can understand others\' emotions in a sports environment', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 3, question: 'I maintain my motivation when facing failure', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 4, question: 'I can manage stress during exercise', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 5, question: 'I welcome constructive feedback', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 6, question: 'I can collaborate effectively with a team', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 7, question: 'I can maintain my motivation over time', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 8, question: 'I can convert negative emotions into positive energy', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 9, question: 'I have good understanding of my strengths and weaknesses', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 10, question: 'I can stay calm in difficult situations', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 11, question: 'I can communicate effectively with coach and teammates', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 12, question: 'I learn from my mistakes and improve', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] }
  ];

  // Exercise Potential Assessment Questions (12 questions)
  const exercisePotentialQuestions = i18n.language === 'fa' ? [
    { id: 1, question: 'من به طور منظم و مستمر تمرین می‌کنم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 2, question: 'من از تمرینات سخت نمی‌ترسم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 3, question: 'من می‌توانم اهداف بلندمدت برای خود تعیین کنم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 4, question: 'من از درد و ناراحتی در تمرینات نمی‌هراسم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 5, question: 'من می‌توانم تمرینات را حتی در شرایط سخت ادامه دهم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 6, question: 'من از یادگیری و بهبود مستمر لذت می‌برم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 7, question: 'من می‌توانم تمرکز خود را در طول تمرین حفظ کنم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 8, question: 'من از رقابت و چالش لذت می‌برم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 9, question: 'من می‌توانم از اشتباهات خود درس بگیرم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 10, question: 'من انگیزه قوی برای پیشرفت دارم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 11, question: 'من می‌توانم با مربی و راهنما همکاری کنم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] },
    { id: 12, question: 'من معتقد هستم که می‌توانم به اهداف ورزشی خود برسم', options: ['کاملاً موافقم', 'موافقم', 'بی‌طرف', 'مخالفم', 'کاملاً مخالفم'] }
  ] : [
    { id: 1, question: 'I exercise regularly and consistently', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 2, question: 'I am not afraid of hard workouts', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 3, question: 'I can set long-term goals for myself', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 4, question: 'I am not afraid of pain and discomfort in workouts', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 5, question: 'I can continue workouts even in difficult conditions', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 6, question: 'I enjoy continuous learning and improvement', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 7, question: 'I can maintain my focus throughout the workout', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 8, question: 'I enjoy competition and challenges', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 9, question: 'I can learn from my mistakes', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 10, question: 'I have strong motivation to progress', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 11, question: 'I can cooperate with coach and guide', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] },
    { id: 12, question: 'I believe I can achieve my sports goals', options: ['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'] }
  ];

  const getQuestions = () => {
    switch (activeTest) {
      case 'personality':
        return exercisePersonalityQuestions;
      case 'eq':
        return eqTestQuestions;
      case 'potential':
        return exercisePotentialQuestions;
      default:
        return [];
    }
  };

  const handleAnswer = (answerIndex) => {
    const questions = getQuestions();
    const questionId = questions[currentQuestion].id;
    setAnswers({ ...answers, [questionId]: answerIndex });
  };

  const handleNext = () => {
    const questions = getQuestions();
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      calculateResults();
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const calculateResults = () => {
    const questions = getQuestions();
    let totalScore = 0;
    let answeredCount = 0;

    questions.forEach(q => {
      if (answers[q.id] !== undefined) {
        // Score: 5 for Strongly Agree, 4 for Agree, 3 for Neutral, 2 for Disagree, 1 for Strongly Disagree
        totalScore += (5 - answers[q.id]);
        answeredCount++;
      }
    });

    const averageScore = answeredCount > 0 ? (totalScore / answeredCount) : 0;
    const percentage = (averageScore / 4) * 100; // Max score is 4 (5-1)

    let level, description;
    if (percentage >= 80) {
      level = i18n.language === 'fa' ? 'عالی' : 'Excellent';
      description = activeTest === 'personality' 
        ? (i18n.language === 'fa' ? 'شما شخصیت ورزشی قوی و منسجم دارید' : 'You have a strong and cohesive sports personality')
        : activeTest === 'eq'
        ? (i18n.language === 'fa' ? 'هوش هیجانی شما در ورزش بسیار بالا است' : 'Your emotional intelligence in sports is very high')
        : (i18n.language === 'fa' ? 'پتانسیل ورزشی شما بسیار بالا است' : 'Your exercise potential is very high');
    } else if (percentage >= 60) {
      level = i18n.language === 'fa' ? 'خوب' : 'Good';
      description = activeTest === 'personality'
        ? (i18n.language === 'fa' ? 'شما شخصیت ورزشی خوبی دارید' : 'You have a good sports personality')
        : activeTest === 'eq'
        ? (i18n.language === 'fa' ? 'هوش هیجانی شما در ورزش خوب است' : 'Your emotional intelligence in sports is good')
        : (i18n.language === 'fa' ? 'پتانسیل ورزشی شما خوب است' : 'Your exercise potential is good');
    } else if (percentage >= 40) {
      level = i18n.language === 'fa' ? 'متوسط' : 'Average';
      description = activeTest === 'personality'
        ? (i18n.language === 'fa' ? 'شخصیت ورزشی شما در سطح متوسط است' : 'Your sports personality is at an average level')
        : activeTest === 'eq'
        ? (i18n.language === 'fa' ? 'هوش هیجانی شما در ورزش متوسط است' : 'Your emotional intelligence in sports is average')
        : (i18n.language === 'fa' ? 'پتانسیل ورزشی شما متوسط است' : 'Your exercise potential is average');
    } else {
      level = i18n.language === 'fa' ? 'نیاز به بهبود' : 'Needs Improvement';
      description = activeTest === 'personality'
        ? (i18n.language === 'fa' ? 'شما نیاز به تقویت شخصیت ورزشی خود دارید' : 'You need to strengthen your sports personality')
        : activeTest === 'eq'
        ? (i18n.language === 'fa' ? 'شما نیاز به بهبود هوش هیجانی خود دارید' : 'You need to improve your emotional intelligence')
        : (i18n.language === 'fa' ? 'شما نیاز به تقویت پتانسیل ورزشی خود دارید' : 'You need to strengthen your exercise potential');
    }

    setResults({
      score: percentage.toFixed(1),
      level,
      description
    });
  };

  const startTest = (testType) => {
    setActiveTest(testType);
    setCurrentQuestion(0);
    setAnswers({});
    setResults({});
  };

  const resetTest = () => {
    setActiveTest(null);
    setCurrentQuestion(0);
    setAnswers({});
    setResults({});
  };

  const questions = getQuestions();
  const currentQ = questions[currentQuestion];

  return (
    <div className="psychology-test" dir="ltr">
      <div className="psychology-test-header">
        <h2>{i18n.language === 'fa' ? 'تست روانشناسی' : 'Psychology Test'}</h2>
      </div>

      {!activeTest ? (
        <div className="test-selection">
          <div className="test-cards">
            <div className="test-card" onClick={() => startTest('personality')}>
              <h3>{i18n.language === 'fa' ? 'آزمون سنجش شخصیت ورزشی' : 'Exercise Personality Assessment'}</h3>
              <p>{i18n.language === 'fa' ? '15 سوال برای تحلیل شخصیت ورزشی شما' : '15 questions to analyze your exercise personality'}</p>
              <button className="start-test-btn">
                {i18n.language === 'fa' ? 'شروع آزمون' : 'Start Test'}
              </button>
            </div>

            <div className="test-card" onClick={() => startTest('eq')}>
              <h3>{i18n.language === 'fa' ? 'تست هوش هیجانی در ورزش' : 'Emotional Intelligence (EQ) Test in Sports'}</h3>
              <p>{i18n.language === 'fa' ? '12 سوال برای سنجش هوش هیجانی شما در محیط ورزشی' : '12 questions to assess your emotional intelligence in sports'}</p>
              <button className="start-test-btn">
                {i18n.language === 'fa' ? 'شروع آزمون' : 'Start Test'}
              </button>
            </div>

            <div className="test-card" onClick={() => startTest('potential')}>
              <h3>{i18n.language === 'fa' ? 'تست سنجش پتانسیل ورزشی' : 'Exercise Potential Assessment'}</h3>
              <p>{i18n.language === 'fa' ? '12 سوال برای ارزیابی پتانسیل ورزشی شما' : '12 questions to evaluate your exercise potential'}</p>
              <button className="start-test-btn">
                {i18n.language === 'fa' ? 'شروع آزمون' : 'Start Test'}
              </button>
            </div>
          </div>
        </div>
      ) : results.score ? (
        <div className="test-results">
          <h3>
            {activeTest === 'personality' 
              ? (i18n.language === 'fa' ? 'نتایج آزمون شخصیت ورزشی' : 'Exercise Personality Results')
              : activeTest === 'eq'
              ? (i18n.language === 'fa' ? 'نتایج تست هوش هیجانی' : 'Emotional Intelligence Results')
              : (i18n.language === 'fa' ? 'نتایج تست پتانسیل ورزشی' : 'Exercise Potential Results')}
          </h3>
          <div className="result-display">
            <div className="result-score">
              <span className="score-number">{results.score}%</span>
              <span className="score-level">{results.level}</span>
            </div>
            <p className="result-description">{results.description}</p>
          </div>
          <button className="retake-test-btn" onClick={resetTest}>
            {i18n.language === 'fa' ? 'بازگشت به منوی اصلی' : 'Back to Main Menu'}
          </button>
        </div>
      ) : (
        <div className="test-taking">
          <div className="test-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
              />
            </div>
            <p className="progress-text">
              {i18n.language === 'fa' 
                ? `سوال ${currentQuestion + 1} از ${questions.length}`
                : `Question ${currentQuestion + 1} of ${questions.length}`}
            </p>
          </div>

          <div className="question-section">
            <h3 className="question-text">{currentQ.question}</h3>
            <div className="options-list">
              {currentQ.options.map((option, index) => (
                <button
                  key={index}
                  className={`option-btn ${answers[currentQ.id] === index ? 'selected' : ''}`}
                  onClick={() => handleAnswer(index)}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>

          <div className="test-navigation">
            <button 
              className="nav-btn prev-btn" 
              onClick={handlePrevious}
              disabled={currentQuestion === 0}
            >
              {i18n.language === 'fa' ? 'قبلی' : 'Previous'}
            </button>
            <button 
              className="nav-btn next-btn" 
              onClick={handleNext}
              disabled={answers[currentQ.id] === undefined}
            >
              {currentQuestion === questions.length - 1
                ? (i18n.language === 'fa' ? 'پایان آزمون' : 'Finish Test')
                : (i18n.language === 'fa' ? 'بعدی' : 'Next')}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PsychologyTest;

