import { useEffect, useState } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";
import "./index.css";

const API_URL = "https://growthpilot-backend-50ms.onrender.com";

function App() {
  const [goal, setGoal] = useState("");
  const [targetSegment, setTargetSegment] = useState("");

  const [experiments, setExperiments] = useState([]);
  const [experiment, setExperiment] = useState(null);

  const [customers, setCustomers] = useState([]);
  const [assignments, setAssignments] = useState([]);

  const [analysis, setAnalysis] = useState(null);
  const [aiRecommendation, setAiRecommendation] = useState(null);

  const [selectedExperiment, setSelectedExperiment] = useState("");

  const [loading, setLoading] = useState(false);
  const [assignmentLoading, setAssignmentLoading] = useState(false);
  const [analysisLoading, setAnalysisLoading] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [runLoading, setRunLoading] = useState(false);
  const [runResult, setRunResult] = useState(null);

  const [aiActions, setAiActions] = useState([]);

  // ============================================================
  // LOAD EXPERIMENTS
  // ============================================================

  const loadExperiments = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/experiments/`
      );

      setExperiments(response.data);
    } catch (err) {
      console.error(
        "Failed to load experiments:",
        err
      );
    }
  };

  // ============================================================
  // LOAD ONLY 100 CUSTOMERS
  // ============================================================

  const loadCustomers = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/customers/?skip=0&limit=100`
      );

      setCustomers(response.data.slice(0, 100));
    } catch (err) {
      console.error(
        "Failed to load customers:",
        err
      );
    }
  };

  // ============================================================
  // LOAD AI ACTIONS
  // ============================================================

  const loadAiActions = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/ai-actions/`
      );

      console.log(
        "AI Actions:",
        response.data
      );

      setAiActions(response.data);
    } catch (err) {
      console.error(
        "AI Actions error:",
        err
      );
    }
  };

  // ============================================================
  // INITIAL LOAD
  // ============================================================

  useEffect(() => {
    loadExperiments();
    loadCustomers();
    loadAiActions();
  }, []);

  // ============================================================
  // GENERATE EXPERIMENT
  // ============================================================

  const generateExperiment = async () => {
    if (!goal || !targetSegment) {
      setError(
        "Please enter both business goal and target segment."
      );
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");
    setExperiment(null);
    setAssignments([]);
    setAnalysis(null);
    setRunResult(null);

    try {
      const response = await axios.post(
        `${API_URL}/generator/`,
        null,
        {
          params: {
            goal: goal,
            target_segment: targetSegment
          }
        }
      );

      console.log(
        "Generated experiment:",
        response.data
      );

      setExperiment(response.data);

      if (response.data.experiment_id) {
        setSelectedExperiment(
          response.data.experiment_id
        );
      } else if (
        response.data.experiment?.experiment_id
      ) {
        setSelectedExperiment(
          response.data.experiment.experiment_id
        );
      }

      await loadExperiments();

      setMessage(
        "Experiment generated successfully!"
      );
    } catch (err) {
      console.error(
        "Generation error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Unable to generate experiment."
      );
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // ACTIVATE EXPERIMENT
  // ============================================================

  const activateExperiment = async () => {
    if (!selectedExperiment) {
      setError(
        "Please select an experiment first."
      );
      return;
    }

    try {
      setError("");
      setMessage("");

      const response = await axios.patch(
        `${API_URL}/experiments/${selectedExperiment}/activate`
      );

      setMessage(
        response.data.message ||
          "Experiment activated successfully!"
      );

      await loadExperiments();

      const updatedExperiment = await axios.get(
        `${API_URL}/experiments/${selectedExperiment}`
      );

      setExperiment(
        updatedExperiment.data
      );
    } catch (err) {
      console.error(
        "Activate error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Failed to activate experiment."
      );
    }
  };

  // ============================================================
  // COMPLETE EXPERIMENT
  // ============================================================

  const completeExperiment = async () => {
    if (!selectedExperiment) {
      setError(
        "Please select an experiment first."
      );
      return;
    }

    try {
      setError("");
      setMessage("");

      const response = await axios.patch(
        `${API_URL}/experiments/${selectedExperiment}/complete`
      );

      setMessage(
        response.data.message ||
          "Experiment completed successfully!"
      );

      await loadExperiments();

      const updatedExperiment = await axios.get(
        `${API_URL}/experiments/${selectedExperiment}`
      );

      setExperiment(
        updatedExperiment.data
      );
    } catch (err) {
      console.error(
        "Complete error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Failed to complete experiment."
      );
    }
  };

  // ============================================================
  // SELECT WINNER
  // ============================================================

  const selectWinner = async () => {
    if (!selectedExperiment) {
      setError(
        "Please select an experiment first."
      );
      return;
    }

    try {
      setError("");
      setMessage("");

      const response = await axios.patch(
        `${API_URL}/experiments/${selectedExperiment}/winner`
      );

      setMessage(
        `Winner selected: ${response.data.winner}`
      );

      await loadExperiments();

      const updatedExperiment = await axios.get(
        `${API_URL}/experiments/${selectedExperiment}`
      );

      setExperiment(
        updatedExperiment.data
      );

      await runAnalysis();
    } catch (err) {
      console.error(
        "Winner selection error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Failed to select winner."
      );
    }
  };

  // ============================================================
  // SELECT EXPERIMENT
  // ============================================================

  const selectExperiment = async (experimentId) => {
    setSelectedExperiment(
      experimentId
    );

    setExperiment(null);
    setAssignments([]);
    setAnalysis(null);
    setAiRecommendation(null);
    setRunResult(null);

    setError("");
    setMessage("");

    if (!experimentId) {
      return;
    }

    try {
      const response = await axios.get(
        `${API_URL}/experiments/${experimentId}`
      );

      console.log(
        "Selected experiment:",
        response.data
      );

      setExperiment(
        response.data
      );

      // ========================================================
      // LOAD ASSIGNMENTS FOR THIS EXPERIMENT
      // ONLY KEEP FIRST 100 IN FRONTEND
      // ========================================================

      try {
        const assignmentsResponse =
          await axios.get(
            `${API_URL}/experiment-assignments/${experimentId}`
          );

        const limitedAssignments =
          Array.isArray(
            assignmentsResponse.data
          )
            ? assignmentsResponse.data.slice(
                0,
                100
              )
            : [];

        setAssignments(
          limitedAssignments
        );

      } catch (assignmentError) {
        console.error(
          "Failed to load assignments:",
          assignmentError
        );

        setAssignments([]);
      }

    } catch (err) {
      console.error(
        "Failed to load selected experiment:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Unable to load experiment."
      );
    }
  };

  // ============================================================
  // ASSIGN 100 CUSTOMERS
  // ============================================================

  const assignCustomers = async () => {
    if (!selectedExperiment) {
      setError(
        "Please select an experiment."
      );
      return;
    }

    setAssignmentLoading(true);
    setError("");
    setMessage("");
    setRunResult(null);

    try {
      const response = await axios.post(
        `${API_URL}/experiment-assignments/auto/${selectedExperiment}`
      );

      console.log(
        "Automatic assignment:",
        response.data
      );

      setMessage(
        response.data.message ||
          "Customers assigned successfully!"
      );

      // ========================================================
      // LOAD ASSIGNMENTS
      // ONLY DISPLAY MAXIMUM 100
      // ========================================================

      const assignmentsResponse =
        await axios.get(
          `${API_URL}/experiment-assignments/${selectedExperiment}`
        );

      const limitedAssignments =
        Array.isArray(
          assignmentsResponse.data
        )
          ? assignmentsResponse.data.slice(
              0,
              100
            )
          : [];

      setAssignments(
        limitedAssignments
      );

    } catch (err) {
      console.error(
        "Assignment error:",
        err
      );

      console.error(
        "Backend response:",
        err.response?.data
      );

      setError(
        err.response?.data?.detail ||
          "Unable to assign customers."
      );

    } finally {
      setAssignmentLoading(false);
    }
  };

  // ============================================================
  // RUN EXPERIMENT
  // ============================================================

  const runExperiment = async () => {
    if (!selectedExperiment) {
      setError(
        "Please select an experiment."
      );
      return;
    }

    if (assignments.length === 0) {
      setError(
        "Please assign customers first."
      );
      return;
    }

    setRunLoading(true);
    setError("");
    setMessage("");
    setRunResult(null);

    try {
      const response = await axios.post(
        `${API_URL}/experiments/${selectedExperiment}/run`
      );

      console.log(
        "Run experiment response:",
        response.data
      );

      setRunResult(
        response.data
      );

      setMessage(
        `Experiment completed successfully! Winner: ${response.data.winner}`
      );

      setExperiment(
        (prev) =>
          prev
            ? {
                ...prev,
                status:
                  response.data.status,
                winner:
                  response.data.winner
              }
            : prev
      );

      await loadExperiments();

      // Refresh analysis after running
      await analyzeExperiment(
        selectedExperiment
      );

    } catch (err) {
      console.error(
        "Run experiment error:",
        err
      );

      console.error(
        "Backend response:",
        err.response?.data
      );

      setError(
        err.response?.data?.detail ||
          "Unable to run experiment."
      );

    } finally {
      setRunLoading(false);
    }
  };

  // ============================================================
  // ANALYZE EXPERIMENT
  // ============================================================

  const analyzeExperiment = async (
    experimentId
  ) => {
    if (!experimentId) {
      return;
    }

    setAnalysisLoading(true);
    setError("");

    try {
      const response = await axios.get(
        `${API_URL}/experiments/${experimentId}/analysis`
      );

      console.log(
        "Analysis:",
        response.data
      );

      setAnalysis(
        response.data
      );

    } catch (error) {
      console.error(
        "Analysis error:",
        error
      );

      setAnalysis(null);

      setError(
        error.response?.data?.detail ||
          "Failed to analyze experiment"
      );

    } finally {
      setAnalysisLoading(false);
    }
  };

  // ============================================================
  // RUN ANALYSIS FOR SELECTED EXPERIMENT
  // ============================================================

  const runAnalysis = async () => {
    if (!selectedExperiment) {
      alert(
        "Please select an experiment first"
      );
      return;
    }

    await analyzeExperiment(
      selectedExperiment
    );
  };

  // ============================================================
  // APPROVE AI ACTION
  // ============================================================

  const approveAction = async (
    actionId
  ) => {
    try {
      const response =
        await axios.put(
          `${API_URL}/ai-actions/${actionId}/approve`
        );

      console.log(
        "Approved:",
        response.data
      );

      setMessage(
        "AI action approved successfully!"
      );

      await loadAiActions();

    } catch (err) {
      console.error(
        "Approve error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Unable to approve AI action."
      );
    }
  };

  // ============================================================
  // EXECUTE AI ACTION
  // ============================================================

  const executeAction = async (
    actionId
  ) => {
    try {
      const response =
        await fetch(
          `${API_URL}/ai-actions/${actionId}/execute`,
          {
            method: "PUT",
            headers: {
              "Content-Type":
                "application/json",
              Accept:
                "application/json"
            }
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        alert(
          data.message ||
            "Failed to execute action"
        );
        return;
      }

      setAiActions(
        (prevActions) =>
          prevActions.map(
            (action) =>
              action.action_id ===
              actionId
                ? {
                    ...action,
                    status:
                      "EXECUTED"
                  }
                : action
          )
      );

      alert(
        "AI action executed successfully"
      );

    } catch (error) {
      console.error(
        "Execute error:",
        error
      );

      alert(
        "Failed to execute action"
      );
    }
  };

  // ============================================================
  // REJECT AI ACTION
  // ============================================================

  const rejectAction = async (
    actionId
  ) => {
    try {
      const response =
        await axios.put(
          `${API_URL}/ai-actions/${actionId}/reject`
        );

      console.log(
        "Rejected:",
        response.data
      );

      setMessage(
        "AI action rejected."
      );

      await loadAiActions();

    } catch (err) {
      console.error(
        "Reject error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Unable to reject AI action."
      );
    }
  };

  // ============================================================
  // ASSIGNMENT COUNTS
  // ============================================================

  const controlCount =
    assignments.filter(
      (assignment) =>
        assignment.group ===
        "CONTROL"
    ).length;

  const variantACount =
    assignments.filter(
      (assignment) =>
        assignment.group ===
        "VARIANT_A"
    ).length;

  const variantBCount =
    assignments.filter(
      (assignment) =>
        assignment.group ===
        "VARIANT_B"
    ).length;

  // ============================================================
  // CHART DATA
  // ============================================================

  const chartData =
    analysis?.groups
      ? Object.entries(
          analysis.groups
        ).map(
          ([group, data]) => ({
            group,
            conversionRate:
              data.conversion_rate
          })
        )
      : [];

  const winner =
    analysis?.winner ||
    runResult?.winner ||
    experiment?.winner ||
    "N/A";

  const winnerRate =
    analysis?.groups?.[winner]
      ?.conversion_rate ?? 0;

  const improvement =
    analysis?.improvement_percent ?? 0;

  // ============================================================
  // SELECTED EXPERIMENT AI ACTIONS
  // ============================================================

  const selectedExperimentActions =
    aiActions.filter(
      (action) =>
        action.experiment_id ===
        selectedExperiment
    );

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div
      className="app"
      style={{
        minHeight: "100vh",
        background: "#f5f7fb",
        padding: "40px",
        fontFamily:
          "Arial, sans-serif"
      }}
    >

      <div
        style={{
          maxWidth: "1100px",
          margin: "0 auto"
        }}
      >

        {/* =====================================================
            HEADER
        ===================================================== */}

        <h1>
          🚀 GrowthPilot
        </h1>

        <div className="navigation-tabs">

          <button
            onClick={() =>
              window.scrollTo({
                top: 0,
                behavior: "smooth"
              })
            }
          >
            🏠 Dashboard
          </button>

          <button
            onClick={() =>
              document
                .getElementById(
                  "experiments-section"
                )
                ?.scrollIntoView({
                  behavior:
                    "smooth"
                })
            }
          >
            🧪 Experiments
          </button>

          <button
            onClick={() =>
              document
                .getElementById(
                  "analysis-section"
                )
                ?.scrollIntoView({
                  behavior:
                    "smooth"
                })
            }
          >
            📊 Analysis
          </button>

          <button
            onClick={() =>
              document
                .getElementById(
                  "ai-actions-section"
                )
                ?.scrollIntoView({
                  behavior:
                    "smooth"
                })
            }
          >
            ⚡ AI Actions
          </button>

          <button
            onClick={() =>
              document
                .getElementById(
                  "history-section"
                )
                ?.scrollIntoView({
                  behavior:
                    "smooth"
                })
            }
          >
            📋 History
          </button>

        </div>

        <p>
          AI-Powered Growth
          Experimentation Platform
        </p>

        <hr />

        {/* =====================================================
            DASHBOARD STATISTICS
        ===================================================== */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(3, 1fr)",
            gap: "20px",
            marginTop: "25px"
          }}
        >

          <div
            style={{
              background: "white",
              padding: "25px",
              borderRadius: "12px",
              textAlign: "center",
              boxShadow:
                "0 2px 8px rgba(0,0,0,0.05)"
            }}
          >
            <h3>
              🧪 Experiments
            </h3>

            <h1>
              {experiments.length}
            </h1>
          </div>

          <div
            style={{
              background: "white",
              padding: "25px",
              borderRadius: "12px",
              textAlign: "center",
              boxShadow:
                "0 2px 8px rgba(0,0,0,0.05)"
            }}
          >
            <h3>
              👥 Customers
            </h3>

            <h1>
              {customers.length}
            </h1>
          </div>

          <div
            style={{
              background: "white",
              padding: "25px",
              borderRadius: "12px",
              textAlign: "center",
              boxShadow:
                "0 2px 8px rgba(0,0,0,0.05)"
            }}
          >
            <h3>
              ⚡ AI Actions
            </h3>

            <h1>
              {aiActions.length}
            </h1>
          </div>

        </div>

        {/* =====================================================
            ERROR
        ===================================================== */}

        {error && (
          <div
            style={{
              background: "#ffe5e5",
              padding: "15px",
              marginTop: "20px",
              borderRadius: "8px",
              color: "#b00020"
            }}
          >
            ❌ {error}
          </div>
        )}

        {/* =====================================================
            SUCCESS
        ===================================================== */}

        {message && (
          <div
            style={{
              background: "#e5ffe9",
              padding: "15px",
              marginTop: "20px",
              borderRadius: "8px"
            }}
          >
            ✅ {message}
          </div>
        )}

        {/* =====================================================
            GENERATE EXPERIMENT
        ===================================================== */}

        <div
          id="experiments-section"
          style={{
            background: "white",
            padding: "25px",
            borderRadius: "12px",
            marginTop: "25px"
          }}
        >

          <h2>
            🧪 Generate Experiment
          </h2>

          <label>
            <strong>
              Business Goal
            </strong>
          </label>

          <input
            type="text"
            placeholder="Increase customer conversion"
            value={goal}
            onChange={(e) =>
              setGoal(
                e.target.value
              )
            }
            style={{
              display: "block",
              width: "100%",
              maxWidth: "600px",
              padding: "12px",
              marginTop: "8px",
              marginBottom: "20px"
            }}
          />

          <label>
            <strong>
              Target Customer Segment
            </strong>
          </label>

          <input
            type="text"
            placeholder="New customers"
            value={targetSegment}
            onChange={(e) =>
              setTargetSegment(
                e.target.value
              )
            }
            style={{
              display: "block",
              width: "100%",
              maxWidth: "600px",
              padding: "12px",
              marginTop: "8px",
              marginBottom: "20px"
            }}
          />

          <button
            onClick={
              generateExperiment
            }
            disabled={loading}
            style={{
              padding:
                "12px 20px",
              cursor:
                "pointer"
            }}
          >
            {loading
              ? "Generating..."
              : "✨ Generate Experiment"}
          </button>

        </div>

        {/* =====================================================
            GENERATED EXPERIMENT
        ===================================================== */}

        {experiment && (
          <div
            style={{
              background: "white",
              padding: "25px",
              borderRadius: "12px",
              marginTop: "25px"
            }}
          >

            {/* =================================================
                EXPERIMENT LIFECYCLE
            ================================================= */}

            <div className="lifecycle-section">

              <div className="lifecycle-header">

                <div>
                  <h3>
                    Experiment Lifecycle
                  </h3>

                  <p>
                    Track the experiment from
                    creation to winner selection.
                  </p>
                </div>

                <div className="status-badge">
                  Status:{" "}
                  {experiment.status ||
                    experiment.experiment?.status ||
                    "DRAFT"}
                </div>

              </div>

              <div className="lifecycle-steps">

                <div className="lifecycle-step">
                  <div className="step-circle">
                    1
                  </div>

                  <span>
                    Draft
                  </span>
                </div>

                <div className="lifecycle-line"></div>

                <div className="lifecycle-step">
                  <div className="step-circle">
                    2
                  </div>

                  <span>
                    Active
                  </span>
                </div>

                <div className="lifecycle-line"></div>

                <div className="lifecycle-step">
                  <div className="step-circle">
                    3
                  </div>

                  <span>
                    Completed
                  </span>
                </div>

                <div className="lifecycle-line"></div>

                <div className="lifecycle-step">
                  <div className="step-circle">
                    4
                  </div>

                  <span>
                    Winner
                  </span>
                </div>

              </div>

              {/* DRAFT */}

              {(experiment.status ===
                "DRAFT" ||
                experiment.experiment?.status ===
                  "DRAFT" ||
                (!experiment.status &&
                  !experiment.experiment?.status)) && (

                <button
                  className="primary-button"
                  onClick={
                    activateExperiment
                  }
                >
                  🚀 Activate Experiment
                </button>

              )}

              {/* ACTIVE */}

              {(experiment.status ===
                "ACTIVE" ||
                experiment.experiment?.status ===
                  "ACTIVE") && (

                <button
                  className="primary-button"
                  onClick={
                    completeExperiment
                  }
                >
                  ✅ Complete Experiment
                </button>

              )}

              {/* COMPLETED */}

              {(experiment.status ===
                "COMPLETED" ||
                experiment.experiment?.status ===
                  "COMPLETED") && (

                <button
                  className="primary-button"
                  onClick={
                    selectWinner
                  }
                >
                  🏆 Select Winner
                </button>

              )}

              {/* WINNER SELECTED */}

              {(experiment.status ===
                "WINNER_SELECTED" ||
                experiment.experiment?.status ===
                  "WINNER_SELECTED") && (

                <div className="winner-display">
                  🏆 Winner:{" "}
                  <strong>
                    {experiment.winner ||
                      experiment.experiment?.winner ||
                      "Not available"}
                  </strong>
                </div>

              )}

            </div>

            {/* =================================================
                GENERATED EXPERIMENT DETAILS
            ================================================= */}

            <h2>
              🤖 Generated Experiment
            </h2>

            <p>
              <strong>
                Name:
              </strong>{" "}
              {experiment.experiment?.name ||
                experiment.name ||
                "Not available"}
            </p>

            <p>
              <strong>
                Hypothesis:
              </strong>{" "}
              {experiment.experiment?.hypothesis ||
                experiment.hypothesis ||
                "Not available"}
            </p>

            <p>
              <strong>
                Objective:
              </strong>{" "}
              {experiment.experiment?.objective ||
                experiment.objective ||
                "Not available"}
            </p>

            <p>
              <strong>
                Target Segment:
              </strong>{" "}
              {experiment.experiment?.target_segment ||
                experiment.target_segment ||
                "Not available"}
            </p>

            <hr />

            <h3>
              CONTROL
            </h3>

            <p>
              {experiment.experiment?.control_description ||
                experiment.control_description ||
                "Not available"}
            </p>

            <h3>
              VARIANT A
            </h3>

            <p>
              {experiment.experiment?.variant_a_description ||
                experiment.variant_a_description ||
                "Not available"}
            </p>

            <h3>
              VARIANT B
            </h3>

            <p>
              {experiment.experiment?.variant_b_description ||
                experiment.variant_b_description ||
                "Not available"}
            </p>

            {/* =================================================
                AI ACTIONS FOR SELECTED EXPERIMENT
            ================================================= */}

            <hr />

            {selectedExperimentActions.length >
              0 && (

              <div
                style={{
                  marginTop: "25px",
                  padding: "20px",
                  background:
                    "#f8f9fa",
                  borderRadius:
                    "12px"
                }}
              >

                <h3>
                  ⚡ AI Growth Actions
                  for This Experiment
                </h3>

                {selectedExperimentActions.map(
                  (action) => (

                    <div
                      key={
                        action.action_id
                      }
                      style={{
                        padding:
                          "15px",
                        marginTop:
                          "12px",
                        background:
                          "white",
                        border:
                          "1px solid #ddd",
                        borderRadius:
                          "10px"
                      }}
                    >

                      <p>
                        <strong>
                          Action:
                        </strong>{" "}
                        {action.action_type}
                      </p>

                      <p>
                        <strong>
                          Recommendation:
                        </strong>{" "}
                        {action.description}
                      </p>

                      <p>
                        <strong>
                          Reason:
                        </strong>{" "}
                        {action.reason}
                      </p>

                      <p>
                        <strong>
                          Status:
                        </strong>{" "}
                        {action.status}
                      </p>

                    </div>

                  )
                )}

              </div>

            )}

          </div>
        )}

        {/* =====================================================
            ASSIGN CUSTOMERS
        ===================================================== */}

        <div
          style={{
            background: "white",
            padding: "25px",
            borderRadius: "12px",
            marginTop: "25px"
          }}
        >

          <h2>
            👥 Assign Customers
          </h2>

          <p>
            Select an experiment and assign
            exactly 100 customers automatically
            across the three experiment groups.
          </p>

          <select
            value={
              selectedExperiment
            }
            onChange={(e) =>
              selectExperiment(
                e.target.value
              )
            }
            style={{
              padding: "12px",
              width: "100%",
              maxWidth: "600px",
              marginBottom: "20px"
            }}
          >

            <option value="">
              -- Select Experiment --
            </option>

            {experiments.map(
              (item) => (

                <option
                  key={
                    item.experiment_id
                  }
                  value={
                    item.experiment_id
                  }
                >
                  {item.experiment_id} -{" "}
                  {item.name}
                </option>

              )
            )}

          </select>

          {/* AVAILABLE CUSTOMERS */}

          <p>
            Customers available:{" "}
            <strong>
              {customers.length}
            </strong>
          </p>

          <button
            onClick={
              assignCustomers
            }
            disabled={
              assignmentLoading ||
              !selectedExperiment
            }
            style={{
              padding:
                "12px 20px",
              cursor:
                "pointer"
            }}
          >
            {assignmentLoading
              ? "Assigning..."
              : "👥 Assign 100 Customers"}
          </button>

          {/* =================================================
              ASSIGNMENT SUMMARY
          ================================================= */}

          {assignments.length >
            0 && (

            <div
              style={{
                marginTop:
                  "25px",
                padding:
                  "20px",
                background:
                  "#f8f9fa",
                borderRadius:
                  "12px"
              }}
            >

              <h3>
                👥 Experiment Customer Assignment
              </h3>

              <div
                style={{
                  display:
                    "grid",
                  gridTemplateColumns:
                    "repeat(4, 1fr)",
                  gap:
                    "15px",
                  marginTop:
                    "15px"
                }}
              >

                <div
                  style={{
                    background:
                      "white",
                    padding:
                      "15px",
                    borderRadius:
                      "10px",
                    textAlign:
                      "center"
                  }}
                >
                  <strong>
                    Total
                  </strong>

                  <h2>
                    {assignments.length}
                  </h2>
                </div>

                <div
                  style={{
                    background:
                      "white",
                    padding:
                      "15px",
                    borderRadius:
                      "10px",
                    textAlign:
                      "center"
                  }}
                >
                  <strong>
                    CONTROL
                  </strong>

                  <h2>
                    {controlCount}
                  </h2>
                </div>

                <div
                  style={{
                    background:
                      "white",
                    padding:
                      "15px",
                    borderRadius:
                      "10px",
                    textAlign:
                      "center"
                  }}
                >
                  <strong>
                    VARIANT A
                  </strong>

                  <h2>
                    {variantACount}
                  </h2>
                </div>

                <div
                  style={{
                    background:
                      "white",
                    padding:
                      "15px",
                    borderRadius:
                      "10px",
                    textAlign:
                      "center"
                  }}
                >
                  <strong>
                    VARIANT B
                  </strong>

                  <h2>
                    {variantBCount}
                  </h2>
                </div>

              </div>

              {/* =================================================
                  CUSTOMER LIST
                  ONLY SHOW MAXIMUM 100
              ================================================= */}

              <details
                style={{
                  marginTop:
                    "20px"
                }}
              >

                <summary
                  style={{
                    cursor:
                      "pointer",
                    fontWeight:
                      "bold"
                  }}
                >
                  View assigned customers
                </summary>

                <div
                  style={{
                    marginTop:
                      "15px",
                    maxHeight:
                      "350px",
                    overflowY:
                      "auto"
                  }}
                >

                  {assignments.map(
                    (assignment) => (

                      <p
                        key={
                          `${assignment.experiment_id}-${assignment.customer_id}`
                        }
                      >

                        {assignment.customer_id}

                        {" → "}

                        <strong>
                          {assignment.group}
                        </strong>

                      </p>

                    )
                  )}

                </div>

              </details>

            </div>

          )}

        </div>

        {/* =====================================================
            RUN EXPERIMENT
        ===================================================== */}

        <div
          className="section"
          style={{
            background:
              "white",
            padding:
              "25px",
            borderRadius:
              "12px",
            marginTop:
              "25px"
          }}
        >

          <h2>
            ⚡ Run Experiment
          </h2>

          <p>
            Run the experiment using the
            assigned customers and automatically
            calculate the winning group.
          </p>

          {assignments.length ===
          0 ? (

            <p>
              Please assign customers before
              running the experiment.
            </p>

          ) : (

            <button
              onClick={
                runExperiment
              }
              disabled={
                runLoading
              }
              style={{
                padding:
                  "14px 24px",
                fontSize:
                  "16px",
                cursor:
                  "pointer"
              }}
            >
              {runLoading
                ? "⏳ Running Experiment..."
                : "⚡ Run Experiment"}
            </button>

          )}

          {runResult && (

            <div
              className="result-card"
              style={{
                marginTop:
                  "20px",
                padding:
                  "20px",
                background:
                  "#f8f9fa",
                borderRadius:
                  "12px"
              }}
            >

              <h3>
                ✅ Experiment Completed
              </h3>

              <p>
                <strong>
                  Winner:
                </strong>{" "}
                {runResult.winner}
              </p>

              <p>
                <strong>
                  Status:
                </strong>{" "}
                {runResult.status}
              </p>

              <p>
                <strong>
                  Results Created:
                </strong>{" "}
                {runResult.results_created}
              </p>

            </div>

          )}

        </div>

        {/* =====================================================
            EXPERIMENT ANALYSIS
        ===================================================== */}

        <div
          id="analysis-section"
          className="section"
          style={{
            background:
              "white",
            padding:
              "25px",
            borderRadius:
              "12px",
            marginTop:
              "25px"
          }}
        >

          <h2>
            📊 Experiment Analysis
          </h2>

          <button
            onClick={
              runAnalysis
            }
            disabled={
              analysisLoading
            }
          >
            {analysisLoading
              ? "Analyzing..."
              : "📊 Analyze Experiment"}
          </button>

          {analysis && (

            <div className="analysis-container">

              <h3>
                Experiment ID:{" "}
                {selectedExperiment}
              </h3>

              {/* CONTROL */}

              <div className="analysis-group">

                <h3>
                  CONTROL
                </h3>

                <p>
                  Customers:{" "}
                  {analysis.control
                    ?.customers ??
                    analysis.groups
                      ?.CONTROL
                      ?.customers ??
                    0}
                </p>

                <p>
                  Conversions:{" "}
                  {analysis.control
                    ?.conversions ??
                    analysis.groups
                      ?.CONTROL
                      ?.conversions ??
                    0}
                </p>

                <p>
                  Conversion Rate:{" "}
                  {analysis.control
                    ?.conversion_rate ??
                    analysis.groups
                      ?.CONTROL
                      ?.conversion_rate ??
                    0}
                  %
                </p>

              </div>

              {/* VARIANT A */}

              <div className="analysis-group">

                <h3>
                  VARIANT A
                </h3>

                <p>
                  Customers:{" "}
                  {analysis.variant_a
                    ?.customers ??
                    analysis.groups
                      ?.VARIANT_A
                      ?.customers ??
                    0}
                </p>

                <p>
                  Conversions:{" "}
                  {analysis.variant_a
                    ?.conversions ??
                    analysis.groups
                      ?.VARIANT_A
                      ?.conversions ??
                    0}
                </p>

                <p>
                  Conversion Rate:{" "}
                  {analysis.variant_a
                    ?.conversion_rate ??
                    analysis.groups
                      ?.VARIANT_A
                      ?.conversion_rate ??
                    0}
                  %
                </p>

              </div>

              {/* VARIANT B */}

              <div className="analysis-group">

                <h3>
                  VARIANT B
                </h3>

                <p>
                  Customers:{" "}
                  {analysis.variant_b
                    ?.customers ??
                    analysis.groups
                      ?.VARIANT_B
                      ?.customers ??
                    0}
                </p>

                <p>
                  Conversions:{" "}
                  {analysis.variant_b
                    ?.conversions ??
                    analysis.groups
                      ?.VARIANT_B
                      ?.conversions ??
                    0}
                </p>

                <p>
                  Conversion Rate:{" "}
                  {analysis.variant_b
                    ?.conversion_rate ??
                    analysis.groups
                      ?.VARIANT_B
                      ?.conversion_rate ??
                    0}
                  %
                </p>

              </div>

              {/* WINNER */}

              <div className="winner">

                <h2>
                  🏆 Winner
                </h2>

                <h1>
                  {analysis.winner ||
                    runResult?.winner ||
                    "N/A"}
                </h1>

                <p>
                  Improvement:{" "}
                  <strong>
                    {analysis.improvement_percent ??
                      0}
                    %
                  </strong>
                </p>

              </div>

              {/* KPI */}

              <div className="kpi-grid">

                <div className="kpi-card">

                  <p>
                    🏆 Winning Variant
                  </p>

                  <h2>
                    {winner}
                  </h2>

                </div>

                <div className="kpi-card">

                  <p>
                    📈 Best Conversion Rate
                  </p>

                  <h2>
                    {winnerRate}%
                  </h2>

                </div>

                <div className="kpi-card">

                  <p>
                    🚀 Improvement
                  </p>

                  <h2>
                    {improvement}%
                  </h2>

                </div>

              </div>

              {/* PERFORMANCE CHART */}

              <div className="performance-chart">

                <h2>
                  📈 Conversion Performance
                </h2>

                {chartData.length >
                0 ? (

                  <ResponsiveContainer
                    width="100%"
                    height={350}
                  >

                    <BarChart
                      data={
                        chartData
                      }
                      margin={{
                        top: 20,
                        right: 30,
                        left: 20,
                        bottom: 20
                      }}
                    >

                      <CartesianGrid
                        strokeDasharray="3 3"
                      />

                      <XAxis
                        dataKey="group"
                      />

                      <YAxis
                        domain={[
                          0,
                          100
                        ]}
                        unit="%"
                      />

                      <Tooltip
                        formatter={(
                          value
                        ) => [
                          `${value}%`,
                          "Conversion Rate"
                        ]}
                      />

                      <Bar
                        dataKey="conversionRate"
                        name="Conversion Rate"
                      />

                    </BarChart>

                  </ResponsiveContainer>

                ) : (

                  <p>
                    No analysis data
                    available for the
                    chart.
                  </p>

                )}

              </div>

              {/* AI RECOMMENDATION */}

              {aiRecommendation && (

                <div className="ai-recommendation">

                  <h2>
                    🤖 AI Growth
                    Recommendation
                  </h2>

                  <h3>
                    Recommendation
                  </h3>

                  <p>
                    {
                      aiRecommendation.recommendation
                    }
                  </p>

                  <h3>
                    Why?
                  </h3>

                  <p>
                    {
                      aiRecommendation.reason
                    }
                  </p>

                </div>

              )}

            </div>

          )}

        </div>

        {/* =====================================================
            AI GROWTH ACTIONS
        ===================================================== */}

        <div
          id="ai-actions-section"
          className="ai-actions-section"
        >

          <h2>
            ⚡ AI Growth Actions
          </h2>

          {aiActions.length ===
          0 ? (

            <p>
              No AI actions available.
            </p>

          ) : (

            aiActions.map(
              (action) => (

                <div
                  key={
                    action.action_id
                  }
                  className="ai-action-card"
                >

                  <h3>
                    {action.action_type}
                  </h3>

                  <p>
                    <strong>
                      Recommendation:
                    </strong>
                  </p>

                  <p>
                    {action.description}
                  </p>

                  <p>
                    <strong>
                      Why?
                    </strong>
                  </p>

                  <p>
                    {action.reason}
                  </p>

                  <p>
                    <strong>
                      Expected Impact:
                    </strong>
                  </p>

                  <p>
                    {action.expected_impact}
                  </p>

                  <p>
                    <strong>
                      Status:
                    </strong>{" "}
                    {action.status}
                  </p>

                  {/* APPROVE / REJECT */}

                  {action.status ===
                    "PROPOSED" && (

                    <div>

                      <button
                        onClick={() =>
                          approveAction(
                            action.action_id
                          )
                        }
                      >
                        ✅ Approve
                      </button>

                      <button
                        onClick={() =>
                          rejectAction(
                            action.action_id
                          )
                        }
                      >
                        ❌ Reject
                      </button>

                    </div>

                  )}

                  {/* EXECUTE */}

                  {action.status ===
                    "APPROVED" && (

                    <button
                      onClick={() =>
                        executeAction(
                          action.action_id
                        )
                      }
                    >
                      ⚡ Execute
                    </button>

                  )}

                  {/* EXECUTING */}

                  {action.status ===
                    "EXECUTING" && (

                    <button disabled>
                      ⏳ Executing...
                    </button>

                  )}

                  {/* EXECUTED */}

                  {action.status ===
                    "EXECUTED" && (

                    <div
                      className="execution-success"
                    >

                      <p>
                        <strong>
                          ✅ Execution Result:
                        </strong>
                      </p>

                      <p>
                        {action.execution_result}
                      </p>

                      <p>
                        <strong>
                          📈 Actual Impact:
                        </strong>
                      </p>

                      <p>
                        {action.actual_impact}
                      </p>

                      {action.executed_at && (

                        <p>
                          <strong>
                            Executed At:
                          </strong>{" "}
                          {new Date(
                            action.executed_at
                          ).toLocaleString()}
                        </p>

                      )}

                    </div>

                  )}

                  {/* FAILED */}

                  {action.status ===
                    "FAILED" && (

                    <div
                      className="execution-failed"
                    >

                      <p>
                        ❌ Execution Failed
                      </p>

                      {action.execution_result && (

                        <p>
                          <strong>
                            Error:
                          </strong>{" "}
                          {action.execution_result}
                        </p>

                      )}

                      {action.actual_impact && (

                        <p>
                          <strong>
                            Actual Impact:
                          </strong>{" "}
                          {action.actual_impact}
                        </p>

                      )}

                    </div>

                  )}

                  {/* REJECTED */}

                  {action.status ===
                    "REJECTED" && (

                    <p>
                      ❌ This AI action was rejected.
                    </p>

                  )}

                </div>

              )
            )

          )}

        </div>

        {/* =====================================================
            EXPERIMENT HISTORY
        ===================================================== */}

        <div
          id="history-section"
          style={{
            background: "white",
            padding: "25px",
            borderRadius: "12px",
            marginTop: "25px"
          }}
        >

          <h2>
            📋 Experiment History
          </h2>

          {experiments.length ===
          0 ? (

            <p>
              No experiments found.
            </p>

          ) : (

            experiments.map(
              (item) => (

                <div
                  key={
                    item.experiment_id
                  }
                  className="history-card"
                >

                  <div className="history-header">

                    <h3>
                      {item.name}
                    </h3>

                    <span className="history-status">
                      {item.status}
                    </span>

                  </div>

                  <p>
                    <strong>
                      ID:
                    </strong>{" "}
                    {
                      item.experiment_id
                    }
                  </p>

                  <p>
                    <strong>
                      Status:
                    </strong>{" "}
                    {item.status}
                  </p>

                  {item.winner && (

                    <p>
                      🏆{" "}
                      <strong>
                        Winner:
                      </strong>{" "}
                      {item.winner}
                    </p>

                  )}

                  {item.created_at && (

                    <p>
                      📅{" "}
                      <strong>
                        Created:
                      </strong>{" "}
                      {new Date(
                        item.created_at
                      ).toLocaleString()}
                    </p>

                  )}

                  <div className="history-actions">

                    <button
                      onClick={() =>
                        selectExperiment(
                          item.experiment_id
                        )
                      }
                    >
                      👁️ View
                    </button>

                    <button
                      onClick={() =>
                        analyzeExperiment(
                          item.experiment_id
                        )
                      }
                      disabled={
                        analysisLoading
                      }
                    >
                      {analysisLoading
                        ? "Analyzing..."
                        : "📊 Analyze"}
                    </button>

                  </div>

                </div>

              )
            )

          )}

        </div>

      </div>
    </div>
  );
}

export default App;