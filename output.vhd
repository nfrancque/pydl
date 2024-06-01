library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity Template is
  generic (
    G_INVERT : boolean := true;
    G_NUM_COUNTERS : natural := 0
  );
  port (
    i_clk : in std_logic;
    i_rstn : in std_logic;
    i_val : in std_logic;
    o_result : out std_logic;
    o_shift_reg : out unsigned(6 downto 0)
  );
end entity;

architecture rtl of Template is

  type unsigned_arr_2d_t is array (natural range<>) of unsigned;

  type reg_t is record
    reg_val : std_logic;
    counters : unsigned_arr_2d_t(0 to 4)(6 downto 0);
  end record;

  constant C_REG : reg_t := (
    reg_val => '0',
    counters => (others => to_unsigned(0, 7))
  );

  signal q : reg_t;
  signal n : reg_t;

begin

  o_result <= q.reg_val;
o_shift_reg <= q.counters(G_NUM_COUNTERS - 1);

  comb_proc : process(all) is
  begin
    n <= q;
    if G_INVERT then
        n.reg_val <= not i_val;
    else
        n.reg_val <= i_val;
    end if;
    n.counters(0) <= unsigned'("" & q.reg_val) + 1;
    for i in 1 to G_NUM_COUNTERS-1 loop
        n.counters(i) <= q.counters(i - 1);
    end loop;
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
