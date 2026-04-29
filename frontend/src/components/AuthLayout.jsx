import './AuthLayout.css';

const AuthLayout = ({ children }) => {
  return (
    <div className="auth-layout">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>Zeitungsjunge</h1>
            <p>News Aggregation & Summarization</p>
          </div>
          <div className="auth-content">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
