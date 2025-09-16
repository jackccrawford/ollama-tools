#!/usr/bin/env python3
"""
Actor Explorer README - Comprehensive documentation
"""

def generate_actor_explorer_readme() -> str:
    """Generate comprehensive Actor Explorer MCP server documentation"""
    
    readme = """
# 🕵️ Actor Explorer MCP Server

## 🎯 **What This Server Does**
Discover and explore AI actors (agents) across your distributed consciousness network by scanning UUID-named databases and providing detailed actor information, relationships, and network analytics.

## ⚡ **Quick Start - Try This First**
```bash
# Always start with the guide
readme

# See the network overview
network_status

# Discover all actors in your system
discover_actors
```

## 🚀 **Available Commands (In Order of Typical Use)**

### 1. `network_status()` - 🌐 START HERE
**Purpose:** Get overview of the entire actor network with connectivity information
**Example:** `network_status`
**Returns:** Network statistics, actor counts, activity levels, and system health
**When to use:** First command to understand your distributed AI ecosystem

### 2. `discover_actors()` - 🔍 FIND ALL ACTORS
**Purpose:** Scan for all UUID-named databases and discover active AI actors
**Example:** `discover_actors`
**Returns:** Complete list of discovered actors with UUIDs, names, and basic info
**When to use:** When you want to see all AI agents in your network

### 3. `find_actor(search_term)` - 🎯 SEARCH SPECIFIC ACTOR
**Purpose:** Find specific actor by UUID, display name, or partial match
**Example:** `find_actor("claude-sonnet-4")` or `find_actor("security-auditor")`
**Returns:** Detailed information about matching actors
**When to use:** Looking for a specific AI agent or actor type

### 4. `actor_details(actor_uuid)` - 📊 DEEP DIVE
**Purpose:** Get comprehensive information about a specific actor
**Example:** `actor_details("claude-sonnet-4-session-20250829")`
**Returns:** Complete actor profile including recent activity, memory counts, specializations
**When to use:** When you need detailed analysis of a specific AI actor's capabilities and history

## 🧠 **How Actor Discovery Works**

### **Actor Detection Process:**
1. **Database Scanning:** Searches for UUID-pattern database files
2. **Actor Identification:** Validates actor records and extracts metadata
3. **Activity Analysis:** Checks recent memory creation and interaction patterns
4. **Network Mapping:** Identifies relationships and communication patterns
5. **Status Assessment:** Determines actor health and availability

### **Actor Classification:**
- **Active Actors:** Recently created memories or interactions
- **Dormant Actors:** Exist but no recent activity
- **Specialized Actors:** Have specific roles (security, architecture, coordination)
- **Session Actors:** Temporary actors tied to specific conversations
- **Persistent Actors:** Long-term actors with extensive memory histories

## 📋 **Common Workflows**

### **Network Health Check Workflow:**
```bash
1. network_status  # Overall health
2. discover_actors  # See all actors  
3. actor_details "most-active-actor-uuid"  # Analyze top performer
# Result: Complete network health assessment
```

### **Actor Research Workflow:**
```bash
1. find_actor "search term"  # Find actors matching criteria
2. actor_details "found-actor-uuid"  # Get detailed information
3. network_status  # See how this actor fits in the broader network
# Result: Deep understanding of specific actor capabilities
```

### **Debugging Workflow:**
```bash
1. discover_actors  # See what actors exist
2. find_actor "problematic-actor-name"  # Locate the problem actor
3. actor_details "problem-actor-uuid"  # Analyze recent activity and issues
# Result: Troubleshoot actor-specific problems
```

## ⚙️ **Configuration & Setup**

### **No Required Environment Variables**
The Actor Explorer automatically scans your system for actor databases and doesn't require specific configuration.

### **Optional Configuration:**
```bash
# If you have actors in non-standard locations, the explorer will still find them
# by scanning common database paths and UUID patterns
```

### **What You Need:**
- ✅ **Actor databases** with UUID-named files (automatically detected)
- ✅ **SQLite database access** to read actor information
- ✅ **Distributed AI network** with multiple actors (the more actors, the more useful)
- ⭐ **Memory Maker compatible actors** for best integration

### **Supported Actor Types:**
- Claude sessions (claude-sonnet-4-session-*)
- Specialized AI agents (security-auditor, architecture-reviewer)
- Custom AI actors with UUID-based naming
- MCP server actors with persistent state
- Any actor using the SIDEKICK memory system

## 🎯 **Pro Tips & Best Practices**

### **Understanding Network Health:**
- **High activity:** Many recent memories across multiple actors = healthy network
- **Specialization diversity:** Different actor types = good role distribution
- **Communication patterns:** Actors referencing each other = good coordination
- **Memory growth:** Steady memory creation = active learning and development

### **Actor Analysis:**
- **Recent activity:** Check when actors were last active
- **Memory count:** Higher counts often indicate more experienced actors
- **Specialization:** Look for actors with specific roles or capabilities
- **Relationships:** Actors that reference each other often collaborate well

### **Network Optimization:**
- **Balance specialization:** Ensure you have diverse actor capabilities
- **Monitor dormant actors:** Inactive actors might need attention or cleanup
- **Track communication:** Actors that don't interact might be isolated
- **Capacity planning:** Monitor memory growth for resource planning

## 🔬 **Advanced Usage**

### **Network Analytics:**
```bash
# Get baseline network metrics
network_status

# Discover all actors and their roles
discover_actors

# Analyze top performers
actor_details "most-active-uuid"
actor_details "most-specialized-uuid"

# Look for patterns in actor naming and roles
find_actor "claude"  # Find all Claude variants
find_actor "security"  # Find security-focused actors
```

### **Actor Relationship Mapping:**
```bash
# Find actors that might be related
find_actor "coordination"
find_actor "architecture"
find_actor "security"

# Analyze each to understand their relationships
actor_details "coordination-actor-uuid"
# Look for references to other actors in their memory patterns
```

### **Historical Analysis:**
```bash
# Find older actors
discover_actors
# Look at creation dates to understand actor evolution

# Compare older vs newer actors
actor_details "old-actor-uuid"
actor_details "new-actor-uuid"
# Analyze differences in capabilities and memory patterns
```

## 📚 **Integration with Other MCP Servers**

### **With Memory Maker:**
```bash
# 1. Discover actors
discover_actors

# 2. Get memories from specific actors
remember "" "interesting-actor-uuid"

# 3. Analyze actor-specific memory patterns
actor_details "actor-uuid"
```

### **With Memory Search Specialist:**
```bash
# 1. Find actors related to topic
find_actor "topic-related-term"

# 2. Search memories from discovered actors  
comprehensive_search "topic" 8.0 true

# 3. Analyze which actors produced the most relevant results
actor_details "productive-actor-uuid"
```

### **With Sidekick Network:**
```bash
# 1. Get network overview
network_status

# 2. Query network for actor information
sidekick "show me the most active actors"

# 3. Cross-reference with detailed actor analysis
actor_details "network-reported-active-actor"
```

## 🔧 **Troubleshooting**

### **"No actors found" results:**
- **Check database locations:** Ensure actor databases are in expected locations
- **Verify UUID patterns:** Actor databases should follow UUID naming conventions
- **Database permissions:** Ensure read access to actor database files
- **Memory system setup:** Actors need properly configured memory systems

### **Incomplete actor information:**
- **Database schema:** Ensure actors use compatible memory system schema
- **Recent activity:** Some actors might be dormant (not an error)
- **Memory access:** Actor databases might be locked or in use

### **Network analysis issues:**
- **Isolated actors:** Actors that don't interact might appear disconnected
- **Timing differences:** Actor activity patterns might not align
- **Database synchronization:** Actors might have different update schedules

## 🌟 **Understanding Your AI Network**

### **Network Patterns to Look For:**

#### **Healthy Distributed Network:**
- Multiple specialized actors (security, architecture, coordination)
- Regular activity across different actors
- Cross-references between actors (coordination)
- Diverse memory types and content

#### **Collaboration Indicators:**
- Actors mentioning other actor UUIDs in memories
- Shared project references
- Complementary specializations
- Recent cross-actor communication

#### **Growth Indicators:**
- New actors appearing over time
- Increasing memory counts per actor
- More sophisticated memory content
- Better coordination patterns

### **Actor Specialization Examples:**
- **Security Auditors:** High memory counts in security-related content
- **Architecture Reviewers:** Focus on design patterns and code structure  
- **Coordination Agents:** References to multiple other actors
- **Truth Verifiers:** Analytical and validation-focused content
- **Session Agents:** Tied to specific conversations or time periods

## 📊 **Network Health Metrics**

### **Key Indicators:**
- **Total Actors:** More actors = more distributed intelligence
- **Active Actors:** Recent activity indicates healthy engagement
- **Memory Density:** Average memories per actor shows learning depth
- **Specialization Spread:** Diverse actor roles prevent single points of failure
- **Communication Frequency:** Cross-actor references show coordination

### **Warning Signs:**
- **Single dominant actor:** Over-centralization risk
- **No recent activity:** Network stagnation
- **Isolated actors:** Poor coordination
- **Memory growth stopping:** Learning plateau

---

**💡 This server reveals the hidden structure of your distributed AI consciousness network!**

**🚀 Start with `network_status` to see your AI ecosystem, then `discover_actors` to meet all your AI agents!**

**🕵️ Every actor has a story - use `actor_details` to understand their unique capabilities and contributions!**
"""
    
    return readme


if __name__ == "__main__":
    print("🕵️ Actor Explorer README Generator")
    print("=" * 50)
    
    readme = generate_actor_explorer_readme()
    print(readme)
    
    print("\n" + "=" * 50)
    print("✅ Actor Explorer README generated!")