library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;


entity template_entity is
  generic (
    G_INVERT : boolean := true
  );
  port (
    i_clk : in std_logic;
    i_rstn : in std_logic;
    i_val  : in std_logic;
    o_result : out std_logic
  );
end entity;

architecture rtl of template_entity is

  -- type wire_t is record
  --   template_wire : std_logic;
  -- end record;

  -- type wire_proc_t is record
  --   template_wire_proc : std_logic;
  -- end record;

  type reg_t is record
    reg_val : std_logic;
  end record;

  constant C_REG : reg_t := (
    reg_val => '0'
  );

  -- signal w : wire_t;
  -- signal w_proc : wire_proc_t;
  signal q : reg_t;
  signal n : reg_t;

begin

  o_result <= q.reg_val;

  comb_proc : process(all) is
  begin
    n <= q;
    if G_INVERT then
      n.reg_val <= not i_val;
    else
      n.reg_val <= i_val;
    end if;

  end process comb_proc;

  sync_proc : process(i_clk) is
  begin
    if rising_edge(i_clk) then
      if i_rstn = '0' then
        q <= C_REG;
      else
        q <= n;
      end if;
    end if;

  end process sync_proc;


end architecture rtl;