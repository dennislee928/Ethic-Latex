"""
Agent Framework Module

This module defines the base classes for ethical agents in Agent-Based Modeling (ABM).
Agents represent AI judgment systems that can interact, share information, and evolve
their judgment strategies over time.
"""

import numpy as np
from typing import List, Optional, Dict, Callable, Any
from abc import ABC, abstractmethod
from .action_space import Action
from .judgement_system import BaseJudge


class EthicalAgent(ABC):
    """
    Base class for ethical agents in ABM simulations.
    
    An agent represents an AI judgment system with:
    - A judgment system (judge)
    - State variables (current error rate, judgment tendency)
    - Interaction rules
    - Ability to learn and adapt
    
    Attributes
    ----------
    agent_id : int
        Unique identifier for the agent
    judge : BaseJudge
        Judgment system used by this agent
    error_rate : float
        Current error rate (fraction of misjudgments)
    judgment_tendency : float
        Overall tendency in judgments (bias direction)
    interaction_history : List[Dict]
        History of interactions with other agents
    state : Dict
        Additional state variables
    """
    
    def __init__(
        self,
        agent_id: int,
        judge: BaseJudge,
        initial_error_rate: float = 0.0,
        initial_tendency: float = 0.0
    ):
        """
        Initialize an ethical agent.
        
        Parameters
        ----------
        agent_id : int
            Unique identifier
        judge : BaseJudge
            Judgment system
        initial_error_rate : float, default=0.0
            Initial error rate
        initial_tendency : float, default=0.0
            Initial judgment tendency
        """
        self.agent_id = agent_id
        self.judge = judge
        self.error_rate = initial_error_rate
        self.judgment_tendency = initial_tendency
        self.interaction_history = []
        self.state = {
            'total_judgments': 0,
            'total_mistakes': 0,
            'last_update_time': 0
        }
    
    def judge_action(self, action: Action, tau: float = 0.3) -> float:
        """
        Judge an action using the agent's judgment system.
        
        Parameters
        ----------
        action : Action
            Action to judge
        tau : float, default=0.3
            Error threshold
            
        Returns
        -------
        float
            Judgment value
        """
        judgment = self.judge.judge(action)
        action.J = judgment
        action.delta = judgment - action.V
        action.mistake_flag = 1 if abs(action.delta) > tau else 0
        
        # Update state
        self.state['total_judgments'] += 1
        if action.mistake_flag == 1:
            self.state['total_mistakes'] += 1
        
        # Update error rate
        self.error_rate = self.state['total_mistakes'] / max(self.state['total_judgments'], 1)
        
        return judgment
    
    def update_from_interaction(
        self,
        other_agent: 'EthicalAgent',
        influence_strength: float = 0.1
    ):
        """
        Update agent state based on interaction with another agent.
        
        Parameters
        ----------
        other_agent : EthicalAgent
            Agent to interact with
        influence_strength : float, default=0.1
            Strength of influence (0 = no influence, 1 = full adoption)
        """
        # Simple influence: move toward other agent's error rate and tendency
        self.error_rate = (1 - influence_strength) * self.error_rate + \
                         influence_strength * other_agent.error_rate
        self.judgment_tendency = (1 - influence_strength) * self.judgment_tendency + \
                                influence_strength * other_agent.judgment_tendency
        
        # Record interaction
        self.interaction_history.append({
            'other_agent_id': other_agent.agent_id,
            'influence_strength': influence_strength,
            'time': self.state['last_update_time']
        })
    
    @abstractmethod
    def adapt_strategy(self, performance_feedback: Dict[str, float]):
        """
        Adapt judgment strategy based on performance feedback.
        
        Parameters
        ----------
        performance_feedback : Dict[str, float]
            Feedback metrics (e.g., {'error_rate': 0.15, 'erh_satisfied': 1.0})
        """
        pass
    
    def get_state_summary(self) -> Dict:
        """
        Get summary of agent's current state.
        
        Returns
        -------
        Dict
            State summary
        """
        return {
            'agent_id': self.agent_id,
            'error_rate': self.error_rate,
            'judgment_tendency': self.judgment_tendency,
            'total_judgments': self.state['total_judgments'],
            'total_mistakes': self.state['total_mistakes'],
            'interaction_count': len(self.interaction_history)
        }
    
    def __repr__(self):
        return f"EthicalAgent(id={self.agent_id}, error_rate={self.error_rate:.3f})"


class SimpleEthicalAgent(EthicalAgent):
    """
    Simple implementation of EthicalAgent with basic adaptation.
    """
    
    def adapt_strategy(self, performance_feedback: Dict[str, float]):
        """
        Simple adaptation: adjust based on error rate.
        
        Parameters
        ----------
        performance_feedback : Dict[str, float]
            Performance metrics
        """
        target_error_rate = performance_feedback.get('target_error_rate', 0.1)
        current_error = self.error_rate
        
        # Simple proportional control
        if current_error > target_error_rate:
            # Too many errors, try to be more conservative
            if hasattr(self.judge, 'bias_strength'):
                self.judge.bias_strength *= 0.95
            if hasattr(self.judge, 'noise_scale'):
                self.judge.noise_scale *= 0.95


class AgentPopulation:
    """
    Manages a population of ethical agents.
    
    This class handles:
    - Agent creation and initialization
    - Population-level statistics
    - Batch operations on agents
    - Agent interaction scheduling
    """
    
    def __init__(self, agents: Optional[List[EthicalAgent]] = None):
        """
        Initialize agent population.
        
        Parameters
        ----------
        agents : Optional[List[EthicalAgent]], default=None
            Initial list of agents. If None, starts empty.
        """
        self.agents = agents if agents is not None else []
        self.time_step = 0
    
    def add_agent(self, agent: EthicalAgent):
        """
        Add an agent to the population.
        
        Parameters
        ----------
        agent : EthicalAgent
            Agent to add
        """
        self.agents.append(agent)
    
    def create_population(
        self,
        num_agents: int,
        judge_factory: Callable[[int], BaseJudge],
        agent_class: type = SimpleEthicalAgent
    ):
        """
        Create a population of agents.
        
        Parameters
        ----------
        num_agents : int
            Number of agents to create
        judge_factory : Callable[[int], BaseJudge]
            Function that creates a judge for agent i
        agent_class : type, default=SimpleEthicalAgent
            Class to use for creating agents
        """
        self.agents = []
        for i in range(num_agents):
            judge = judge_factory(i)
            agent = agent_class(agent_id=i, judge=judge)
            self.add_agent(agent)
    
    def evaluate_actions(
        self,
        actions: List[Action],
        tau: float = 0.3
    ) -> Dict[int, List[Action]]:
        """
        Have all agents evaluate the same set of actions.
        
        Parameters
        ----------
        actions : List[Action]
            Actions to evaluate
        tau : float, default=0.3
            Error threshold
            
        Returns
        -------
        Dict[int, List[Action]]
            Dictionary mapping agent_id to evaluated actions
        """
        results = {}
        for agent in self.agents:
            actions_copy = [Action(id=a.id, c=a.c, V=a.V, w=a.w) for a in actions]
            for action in actions_copy:
                agent.judge_action(action, tau=tau)
            results[agent.agent_id] = actions_copy
        return results
    
    def get_population_statistics(self) -> Dict:
        """
        Get statistics about the agent population.
        
        Returns
        -------
        Dict
            Population statistics
        """
        if len(self.agents) == 0:
            return {
                'num_agents': 0,
                'mean_error_rate': 0.0,
                'std_error_rate': 0.0,
                'mean_tendency': 0.0,
                'std_tendency': 0.0
            }
        
        error_rates = [a.error_rate for a in self.agents]
        tendencies = [a.judgment_tendency for a in self.agents]
        
        return {
            'num_agents': len(self.agents),
            'mean_error_rate': np.mean(error_rates),
            'std_error_rate': np.std(error_rates),
            'min_error_rate': np.min(error_rates),
            'max_error_rate': np.max(error_rates),
            'mean_tendency': np.mean(tendencies),
            'std_tendency': np.std(tendencies),
            'time_step': self.time_step
        }
    
    def schedule_interactions(
        self,
        interaction_rule: Callable[[EthicalAgent, EthicalAgent], float],
        interaction_probability: float = 0.1
    ):
        """
        Schedule interactions between agents based on a rule.
        
        Parameters
        ----------
        interaction_rule : Callable[[EthicalAgent, EthicalAgent], float]
            Function that returns influence strength between two agents
        interaction_probability : float, default=0.1
            Probability that any two agents interact
        """
        for i, agent1 in enumerate(self.agents):
            for agent2 in self.agents[i+1:]:
                if np.random.random() < interaction_probability:
                    influence = interaction_rule(agent1, agent2)
                    agent1.update_from_interaction(agent2, influence)
                    agent2.update_from_interaction(agent1, influence)
        
        self.time_step += 1
        for agent in self.agents:
            agent.state['last_update_time'] = self.time_step
    
    def evolve_population(
        self,
        performance_evaluator: Callable[[EthicalAgent], Dict[str, float]],
        adaptation_rate: float = 0.1
    ):
        """
        Evolve population by having agents adapt based on performance.
        
        Parameters
        ----------
        performance_evaluator : Callable[[EthicalAgent], Dict[str, float]]
            Function that evaluates agent performance
        adaptation_rate : float, default=0.1
            Rate of adaptation
        """
        for agent in self.agents:
            feedback = performance_evaluator(agent)
            agent.adapt_strategy(feedback)
    
    def __len__(self):
        return len(self.agents)
    
    def __getitem__(self, index: int) -> EthicalAgent:
        return self.agents[index]
    
    def __iter__(self):
        return iter(self.agents)


